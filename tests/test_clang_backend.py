from __future__ import annotations

from pathlib import Path

import pytest

from uzcy import clang_backend


def test_find_compile_db_when_direct_exists_then_returns(tmp_path: Path) -> None:
    path = tmp_path / "compile_commands.json"
    path.write_text("{}", encoding="utf-8")
    found = clang_backend.find_compile_db(tmp_path)
    assert found == path, "Should return compile_commands.json at root"


def test_find_compile_db_when_nested_then_returns(tmp_path: Path) -> None:
    nested = tmp_path / "build" / "compile_commands.json"
    nested.parent.mkdir()
    nested.write_text("{}", encoding="utf-8")
    found = clang_backend.find_compile_db(tmp_path)
    assert found == nested, "Should return nested compile_commands.json when root missing"


def test_ensure_clang_scan_deps_when_missing_then_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(clang_backend.shutil, "which", lambda _: None)
    with pytest.raises(FileNotFoundError, match="clang-scan-deps not found"):
        clang_backend._ensure_clang_scan_deps()


def test_ensure_clang_scan_deps_when_found_then_returns(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(clang_backend.shutil, "which", lambda _: "/usr/bin/clang-scan-deps")
    tool = clang_backend._ensure_clang_scan_deps()
    assert tool == "/usr/bin/clang-scan-deps", "Should return tool path when found"


def test_run_clang_scan_deps_when_success_then_returns_stdout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_run(*_args: object, **_kwargs: object) -> object:
        class Result:
            returncode = 0
            stdout = "ok"
            stderr = ""

        return Result()

    monkeypatch.setattr(clang_backend, "_ensure_clang_scan_deps", lambda: "clang-scan-deps")
    monkeypatch.setattr(clang_backend.subprocess, "run", fake_run)
    output = clang_backend.run_clang_scan_deps(Path("compile_commands.json"))
    assert output == "ok", "Should return stdout from clang-scan-deps"


def test_run_clang_scan_deps_when_failure_then_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(*_args: object, **_kwargs: object) -> object:
        class Result:
            returncode = 1
            stdout = ""
            stderr = "boom"

        return Result()

    monkeypatch.setattr(clang_backend, "_ensure_clang_scan_deps", lambda: "clang-scan-deps")
    monkeypatch.setattr(clang_backend.subprocess, "run", fake_run)
    with pytest.raises(RuntimeError, match="boom"):
        clang_backend.run_clang_scan_deps(Path("compile_commands.json"))


def test_decode_json_stream_when_multiple_objects_then_returns_list() -> None:
    raw = '{"a": 1} {"b": 2}'
    items = clang_backend._decode_json_stream(raw)
    assert items == [{"a": 1}, {"b": 2}], "Should decode concatenated JSON objects"


def test_load_json_when_invalid_json_then_stream_decode() -> None:
    raw = '{"a": 1}{"b": 2}'
    data = clang_backend._load_json(raw)
    assert data == [{"a": 1}, {"b": 2}], "Should fall back to stream decoding"


def test_normalize_entries_when_translation_units_then_returns_list() -> None:
    data = {"translation-units": [{"input-file": "a.c"}]}
    entries = clang_backend._normalize_entries(data)
    assert entries == [{"input-file": "a.c"}], "Should extract translation-units list"


def test_extract_paths_when_mixed_entries_then_returns_strings() -> None:
    values = ["a.h", {"file": "b.h"}, {"path": "c.h"}]
    paths = clang_backend._extract_paths(values)
    assert paths == ["a.h", "b.h", "c.h"], "Should extract string paths"


def test_pick_deps_when_direct_deps_present_then_returns() -> None:
    entry = {"direct-deps": ["a.h", "b.h"]}
    deps = clang_backend._pick_deps(entry)
    assert deps == ["a.h", "b.h"], "Should pick direct dependencies"


def test_pick_deps_when_direct_missing_then_fallback() -> None:
    entry = {"dependencies": [{"file": "a.h"}]}
    deps = clang_backend._pick_deps(entry)
    assert deps == ["a.h"], "Should fall back to other dependency keys"


def test_parse_clang_scan_deps_when_valid_then_returns_map() -> None:
    raw = '{"input-file": "a.c", "direct-deps": ["b.h"]}'
    parsed = clang_backend.parse_clang_scan_deps(raw)
    assert parsed == {"a.c": ["b.h"]}, "Should parse clang-scan-deps output"
