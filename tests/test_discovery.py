from __future__ import annotations

from pathlib import Path

from uzcy.discovery import _filter_dirs, discover_files, is_excluded


def test_is_excluded_when_pattern_in_parts_then_true(tmp_path: Path) -> None:
    root = tmp_path
    path = root / "build" / "main.c"
    path.parent.mkdir()
    path.write_text("", encoding="utf-8")
    assert is_excluded(path, root, ["build"]), "Directory part should exclude path"


def test_is_excluded_when_glob_matches_then_true(tmp_path: Path) -> None:
    root = tmp_path
    path = root / "gen" / "file.gen"
    path.parent.mkdir()
    path.write_text("", encoding="utf-8")
    assert is_excluded(path, root, ["**/*.gen"]), "Glob pattern should exclude path"


def test_is_excluded_when_no_match_then_false(tmp_path: Path) -> None:
    root = tmp_path
    path = root / "src" / "main.c"
    path.parent.mkdir()
    path.write_text("", encoding="utf-8")
    assert not is_excluded(path, root, ["build"]), "Non-matching pattern should not exclude"


def test_filter_dirs_when_excluded_then_removed(tmp_path: Path) -> None:
    root = tmp_path
    dirpath = root
    dirnames = ["build", "src"]
    _filter_dirs(root, dirpath, dirnames, ["build"])
    assert dirnames == ["src"], "Excluded directories should be removed in-place"


def test_discover_files_when_empty_then_returns_empty(tmp_path: Path) -> None:
    found = discover_files(tmp_path, ["build"], [".c"])
    assert found == [], "Empty tree should return no files"


def test_discover_files_when_extensions_and_excludes_then_filters(tmp_path: Path) -> None:
    root = tmp_path
    (root / "src").mkdir()
    (root / "build").mkdir()
    (root / "src" / "main.c").write_text("", encoding="utf-8")
    (root / "src" / "skip.txt").write_text("", encoding="utf-8")
    (root / "build" / "generated.c").write_text("", encoding="utf-8")
    found = discover_files(root, ["build"], [".c"])
    assert found == [root / "src" / "main.c"], "Should include only matching extensions"
