from __future__ import annotations

from pathlib import Path

from uzcy.writer import (
    apply_block,
    detect_newline,
    find_block,
    find_insert_index,
    format_used_by_block,
    read_text,
    update_file,
    write_atomic,
    write_backup,
)


def test_detect_newline_when_crlf_then_returns_crlf() -> None:
    newline = detect_newline(b"a\r\n")
    assert newline == "\r\n", "Should detect CRLF newlines"


def test_detect_newline_when_lf_then_returns_lf() -> None:
    newline = detect_newline(b"a\n")
    assert newline == "\n", "Should default to LF newlines"


def test_read_text_when_trailing_newline_then_true(tmp_path: Path) -> None:
    path = tmp_path / "file.c"
    path.write_text("line\n", encoding="utf-8")
    _, _, trailing = read_text(path)
    assert trailing, "Trailing newline should be detected"


def test_read_text_when_no_trailing_newline_then_false(tmp_path: Path) -> None:
    path = tmp_path / "file.c"
    path.write_text("line", encoding="utf-8")
    _, _, trailing = read_text(path)
    assert not trailing, "Missing trailing newline should be detected"


def test_format_used_by_block_when_paths_then_formats() -> None:
    lines = format_used_by_block(["a.c", "b.h"])
    assert lines[0] == "// <used_by>", "Block should start with marker"
    assert lines[-1] == "// </used_by>", "Block should end with marker"


def test_find_block_when_present_then_returns_indices() -> None:
    lines = ["// <used_by>", "// - a.c", "// </used_by>"]
    found = find_block(lines)
    assert found == (0, 2), "Should return start and end indices"


def test_find_block_when_missing_then_none() -> None:
    found = find_block(["int x;"])
    assert found is None, "Should return None when block missing"


def test_find_insert_index_when_line_banner_then_after_banner() -> None:
    lines = ["// banner", "// more", "", "int x;"]
    index = find_insert_index(lines)
    assert index == 3, "Should insert after line comment banner"


def test_find_insert_index_when_block_banner_then_after_banner() -> None:
    lines = ["/*", " * banner", " */", "", "int x;"]
    index = find_insert_index(lines)
    assert index == 4, "Should insert after block comment banner"


def test_apply_block_when_insert_then_adds_block() -> None:
    lines = ["int x;"]
    block = ["// <used_by>", "// - a.c", "// </used_by>"]
    updated = apply_block(lines, block)
    assert updated[0] == "// <used_by>", "Should insert block at top"


def test_apply_block_when_replace_then_updates_block() -> None:
    lines = ["// <used_by>", "// - old.c", "// </used_by>", "int x;"]
    block = ["// <used_by>", "// - new.c", "// </used_by>"]
    updated = apply_block(lines, block)
    assert "// - new.c" in updated, "Should replace existing block"


def test_apply_block_when_remove_then_deletes_block() -> None:
    lines = ["// <used_by>", "// - old.c", "// </used_by>", "int x;"]
    updated = apply_block(lines, None)
    assert "// <used_by>" not in updated, "Should remove used_by block"


def test_write_atomic_when_called_then_writes(tmp_path: Path) -> None:
    path = tmp_path / "file.c"
    path.write_text("old", encoding="utf-8")
    write_atomic(path, "new")
    assert path.read_text(encoding="utf-8") == "new", "Atomic write should update file"


def test_write_backup_when_called_then_creates_copy(tmp_path: Path) -> None:
    root = tmp_path
    path = root / "src" / "file.c"
    path.parent.mkdir(parents=True)
    path.write_text("data", encoding="utf-8")
    backup_dir = tmp_path / "backup"
    write_backup(path, root, backup_dir)
    backup_path = backup_dir / "src" / "file.c"
    assert backup_path.exists(), "Backup file should be created"
    assert backup_path.read_text(encoding="utf-8") == "data", "Backup should match source"


def test_update_file_when_dry_run_then_no_write(tmp_path: Path) -> None:
    path = tmp_path / "file.c"
    path.write_text("int x;\n", encoding="utf-8")
    changed = update_file(path, ["a.c"], True, None, tmp_path)
    assert changed, "Dry run should report a change"
    assert path.read_text(encoding="utf-8") == "int x;\n", "Dry run should not write"


def test_update_file_when_no_change_then_false(tmp_path: Path) -> None:
    path = tmp_path / "file.c"
    path.write_text("// <used_by>\n// - a.c\n// </used_by>\n", encoding="utf-8")
    changed = update_file(path, ["a.c"], False, None, tmp_path)
    assert not changed, "Should return False when content unchanged"


def test_update_file_when_crlf_then_preserves_newlines(tmp_path: Path) -> None:
    path = tmp_path / "file.c"
    path.write_bytes(b"int x;\r\n")
    update_file(path, ["a.c"], False, None, tmp_path)
    data = path.read_bytes()
    assert b"\r\n" in data, "Should preserve CRLF line endings"
    assert b"\n" not in data.replace(b"\r\n", b""), "Should avoid bare LF endings"
