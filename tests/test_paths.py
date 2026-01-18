from __future__ import annotations

from pathlib import Path

from uzcy.paths import abs_path, relative_posix


def test_abs_path_when_relative_then_resolves() -> None:
    rel = Path("somefile.txt")
    resolved = abs_path(rel)
    assert resolved.is_absolute(), "abs_path should return an absolute path"
    assert resolved.name == "somefile.txt", "abs_path should preserve the filename"


def test_abs_path_when_absolute_then_preserves_location(tmp_path: Path) -> None:
    target = tmp_path / "file.c"
    resolved = abs_path(target)
    assert resolved == target.resolve(), "abs_path should resolve absolute paths"


def test_relative_posix_when_under_root_then_returns_relative(tmp_path: Path) -> None:
    root = tmp_path
    file_path = root / "src" / "main.c"
    file_path.parent.mkdir()
    file_path.write_text("", encoding="utf-8")
    rel = relative_posix(file_path, root)
    assert rel == "src/main.c", "relative_posix should return root-relative POSIX paths"


def test_relative_posix_when_outside_root_then_returns_absolute(tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    outsider = tmp_path / "other" / "file.c"
    outsider.parent.mkdir()
    outsider.write_text("", encoding="utf-8")
    rel = relative_posix(outsider, root)
    assert rel.startswith("/"), "relative_posix should return absolute POSIX paths for outsiders"
