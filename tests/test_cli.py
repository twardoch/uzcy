from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from uzcy import cli
from uzcy.config import DEFAULT_EXCLUDES, UzcyConfig


def test_setup_logging_when_called_then_no_error() -> None:
    cli._setup_logging(False)
    cli._setup_logging(True)
    assert True, "Logging setup should not raise"


def test_parse_excludes_when_none_then_defaults() -> None:
    parsed = cli._parse_excludes(None)
    assert parsed == DEFAULT_EXCLUDES, "None should yield default excludes"


def test_parse_excludes_when_empty_then_empty_list() -> None:
    parsed = cli._parse_excludes("")
    assert parsed == [], "Empty string should disable excludes"


def test_parse_excludes_when_values_then_split() -> None:
    parsed = cli._parse_excludes("a, b, ,c")
    assert parsed == ["a", "b", "c"], "Should split and trim excludes"


def test_resolve_compile_db_when_config_has_path_then_returns_abs(tmp_path: Path) -> None:
    db = tmp_path / "compile_commands.json"
    db.write_text("{}", encoding="utf-8")
    config = UzcyConfig(path=tmp_path, compile_db=db, exclude=[])
    resolved = cli._resolve_compile_db(config, tmp_path)
    assert resolved == db.resolve(), "Should return absolute compile db path"


def test_resolve_compile_db_when_none_then_finds(tmp_path: Path) -> None:
    db = tmp_path / "compile_commands.json"
    db.write_text("{}", encoding="utf-8")
    config = UzcyConfig(path=tmp_path, compile_db=None, exclude=[])
    resolved = cli._resolve_compile_db(config, tmp_path)
    assert resolved == db, "Should discover compile_commands.json"


def test_run_clang_backend_when_parsers_then_returns_forward(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sentinel = {Path("a.c"): [Path("b.h")]}
    monkeypatch.setattr(cli, "run_clang_scan_deps", lambda _db: "raw")
    monkeypatch.setattr(cli, "parse_clang_scan_deps", lambda _raw: {"a.c": ["b.h"]})
    monkeypatch.setattr(cli, "build_forward_from_clang", lambda _raw, _files: sentinel)
    result = cli._run_clang_backend([Path("a.c")], Path("compile_commands.json"))
    assert result == sentinel, "Should return forward map from clang backend"


def test_run_text_backend_when_called_then_returns_forward(monkeypatch: pytest.MonkeyPatch) -> None:
    sentinel = {Path("a.c"): []}
    monkeypatch.setattr(cli, "build_text_forward_map", lambda _files: sentinel)
    result = cli._run_text_backend([Path("a.c")])
    assert result == sentinel, "Should return forward map from text backend"


def test_select_forward_map_when_mode_text_then_uses_text(monkeypatch: pytest.MonkeyPatch) -> None:
    sentinel = {Path("a.c"): []}
    config = UzcyConfig(path=Path(), mode="text", exclude=[])
    monkeypatch.setattr(cli, "_run_text_backend", lambda _files: sentinel)
    result = cli._select_forward_map(config, [Path("a.c")], Path())
    assert result == sentinel, "Text mode should use text backend"


def test_select_forward_map_when_mode_clang_missing_db_then_raises(tmp_path: Path) -> None:
    config = UzcyConfig(path=tmp_path, mode="clang", exclude=[])
    with pytest.raises(FileNotFoundError, match=r"compile_commands\.json not found"):
        cli._select_forward_map(config, [], tmp_path)


def test_select_forward_map_when_auto_with_db_then_clang(monkeypatch: pytest.MonkeyPatch) -> None:
    sentinel = {Path("a.c"): []}
    config = UzcyConfig(path=Path(), mode="auto", exclude=[])
    monkeypatch.setattr(cli, "_resolve_compile_db", lambda _c, _r: Path("db"))
    monkeypatch.setattr(cli, "_run_clang_backend", lambda _files, _db: sentinel)
    result = cli._select_forward_map(config, [Path("a.c")], Path())
    assert result == sentinel, "Auto mode should use clang when available"


def test_select_forward_map_when_clang_fails_then_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    sentinel = {Path("a.c"): []}
    config = UzcyConfig(path=Path(), mode="auto", exclude=[])
    monkeypatch.setattr(cli, "_resolve_compile_db", lambda _c, _r: Path("db"))
    monkeypatch.setattr(
        cli, "_run_clang_backend", lambda _files, _db: (_ for _ in ()).throw(RuntimeError("boom"))
    )
    monkeypatch.setattr(cli, "_run_text_backend", lambda _files: sentinel)
    result = cli._select_forward_map(config, [Path("a.c")], Path())
    assert result == sentinel, "Auto mode should fall back to text on error"


def test_format_used_by_when_paths_then_relative(tmp_path: Path) -> None:
    root = tmp_path
    file_path = root / "a.c"
    result = cli._format_used_by([file_path], root)
    assert result == ["a.c"], "Should format used_by paths as relative POSIX"


def test_build_config_when_values_then_sets_fields(tmp_path: Path) -> None:
    config = cli._build_config(
        path=str(tmp_path),
        compile_db=str(tmp_path / "compile_commands.json"),
        mode="text",
        exclude="a,b",
        dry_run=True,
        backup=str(tmp_path / "backup"),
        verbose=True,
    )
    assert config.mode == "text", "Mode should be set"
    assert config.dry_run, "Dry run flag should be set"
    assert config.exclude == ["a", "b"], "Exclude list should be parsed"


def test_run_with_config_when_files_then_updates(tmp_path: Path) -> None:
    header = tmp_path / "a.h"
    source = tmp_path / "b.c"
    header.write_text("int x;\n", encoding="utf-8")
    source.write_text('#include "a.h"\n', encoding="utf-8")
    config = UzcyConfig(path=tmp_path, mode="text", exclude=[])
    cli._run_with_config(config)
    updated = header.read_text(encoding="utf-8")
    assert "// <used_by>" in updated, "Header should get used_by block"
    assert "// - b.c" in updated, "Header should list the user file"


def test_run_when_called_then_passes_config(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    called: dict[str, UzcyConfig] = {}

    def fake_run(config: UzcyConfig) -> None:
        called["config"] = config

    monkeypatch.setattr(cli, "_run_with_config", fake_run)
    cli.run(path=str(tmp_path), mode="text")
    assert "config" in called, "run should call _run_with_config"


def test_main_when_called_then_invokes_fire(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_fire(arg: object) -> None:
        captured["arg"] = arg

    monkeypatch.setattr(cli.fire, "Fire", fake_fire)
    cli.main()
    assert "run" in captured["arg"], "main should expose run command"


def test_run_when_examples_then_matches_expected(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    source = root / "examples" / "simple"
    expected = root / "examples" / "simple_expected"
    target = tmp_path / "simple"
    shutil.copytree(source, target)
    cli.run(path=str(target), mode="text")
    for name in ["a.h", "b.c", "c.cpp"]:
        actual_text = (target / name).read_text(encoding="utf-8")
        expected_text = (expected / name).read_text(encoding="utf-8")
        assert actual_text == expected_text, f"Updated {name} should match expected"
