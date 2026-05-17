"""Safe, idempotent used_by block updates."""

from __future__ import annotations

import tempfile
from pathlib import Path

from loguru import logger

from uzcy.paths import relative_posix


def detect_newline(data: bytes) -> str:
    return "\r\n" if b"\r\n" in data else "\n"


def read_text(path: Path) -> tuple[str, str, bool]:
    data = path.read_bytes()
    newline = detect_newline(data)
    text = data.decode("utf-8", errors="ignore")
    trailing = text.endswith("\n") or text.endswith("\r\n")
    return text, newline, trailing


def format_used_by_block(paths: list[str]) -> list[str]:
    lines = ["// <used_by>"]
    for path in paths:
        lines.append(f"// - {path}")
    lines.append("// </used_by>")
    return lines


def find_block(lines: list[str]) -> tuple[int, int] | None:
    start = None
    for index, line in enumerate(lines):
        if line.strip() == "// <used_by>":
            start = index
            break
    if start is None:
        return None
    for index in range(start + 1, len(lines)):
        if lines[index].strip() == "// </used_by>":
            return start, index
    return None


def _skip_leading_blank(lines: list[str]) -> int:
    index = 0
    while index < len(lines) and lines[index].strip() == "":
        index += 1
    return index


def _skip_blank_from(lines: list[str], index: int) -> int:
    while index < len(lines) and lines[index].strip() == "":
        index += 1
    return index


def find_insert_index(lines: list[str]) -> int:
    index = _skip_leading_blank(lines)
    if index >= len(lines):
        return 0
    line = lines[index].lstrip()
    if line.startswith("//"):
        while index < len(lines) and lines[index].lstrip().startswith("//"):
            index += 1
        return _skip_blank_from(lines, index)
    if line.startswith("/*"):
        while index < len(lines):
            if "*/" in lines[index]:
                return _skip_blank_from(lines, index + 1)
            index += 1
    return 0


def _ensure_gap(block_lines: list[str], next_line: str | None) -> list[str]:
    if next_line is None or next_line.strip() == "":
        return block_lines
    return block_lines + [""]


def apply_block(lines: list[str], block_lines: list[str] | None) -> list[str]:
    found = find_block(lines)
    if not block_lines and not found:
        return lines
    if found and not block_lines:
        start, end = found
        return lines[:start] + lines[end + 1 :]
    if found and block_lines:
        start, end = found
        return lines[:start] + block_lines + lines[end + 1 :]
    index = find_insert_index(lines)
    next_line = lines[index] if index < len(lines) else None
    block_lines = _ensure_gap(block_lines or [], next_line)
    return lines[:index] + block_lines + lines[index:]


def write_atomic(path: Path, text: str) -> None:
    tmp_dir = path.parent
    with tempfile.NamedTemporaryFile("w", delete=False, dir=tmp_dir, encoding="utf-8") as tmp:
        tmp.write(text)
        tmp_path = Path(tmp.name)
    tmp_path.replace(path)


def write_backup(path: Path, root: Path, backup_dir: Path) -> None:
    backup_path = backup_dir / relative_posix(path, root)
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    backup_path.write_bytes(path.read_bytes())


def update_file(
    path: Path,
    used_by: list[str],
    dry_run: bool,
    backup_dir: Path | None,
    root: Path,
) -> bool:
    text, newline, trailing = read_text(path)
    lines = text.splitlines()
    block_lines = format_used_by_block(used_by) if used_by else None
    updated_lines = apply_block(lines, block_lines)
    if updated_lines == lines:
        return False
    updated_text = newline.join(updated_lines) + (newline if trailing else "")
    if dry_run:
        logger.info("Would update {}", path)
        return True
    if backup_dir:
        write_backup(path, root, backup_dir)
    write_atomic(path, updated_text)
    return True
