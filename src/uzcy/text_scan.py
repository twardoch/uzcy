# this_file: src/uzcy/text_scan.py
"""Text-based include scanning fallback.

This backend reads ``#include`` lines directly instead of asking a compiler.
It needs no ``compile_commands.json``, so it works anywhere, but it cannot
resolve includes the way a preprocessor would: it matches by path suffix or
basename and skips any include that matches more than one known file. Trade
accuracy for reach — use the clang backend when a compile database exists.
"""

from __future__ import annotations

import re
from pathlib import Path

from loguru import logger

INCLUDE_RE = re.compile(r"^\s*#\s*include\s*[<\"]([^\">]+)[\">]")


def _strip_block_comment(line: str, in_block: bool) -> tuple[str, bool]:
    if in_block:
        end = line.find("*/")
        if end == -1:
            return "", True
        line = line[end + 2 :]
        in_block = False
    while "/*" in line:
        start = line.find("/*")
        end = line.find("*/", start + 2)
        if end == -1:
            return line[:start], True
        line = line[:start] + line[end + 2 :]
    return line, in_block


def _strip_line_comment(line: str) -> str:
    if "//" in line:
        return line.split("//", 1)[0]
    return line


def scan_includes(text: str) -> list[str]:
    """Return include targets found in source text."""
    includes: list[str] = []
    in_block = False
    for line in text.splitlines():
        cleaned, in_block = _strip_block_comment(line, in_block)
        if in_block:
            continue
        cleaned = _strip_line_comment(cleaned)
        match = INCLUDE_RE.match(cleaned)
        if match:
            includes.append(match.group(1))
    return includes


def scan_includes_from_file(path: Path) -> list[str]:
    """Read a file and return include targets."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    return scan_includes(text)


def resolve_include(include: str, files: list[Path]) -> list[Path]:
    """Resolve an include to matching file paths by suffix or basename."""
    by_suffix = [path for path in files if path.as_posix().endswith(include)]
    if by_suffix:
        return by_suffix
    basename = Path(include).name
    return [path for path in files if path.name == basename]


def build_text_forward_map(files: list[Path]) -> dict[Path, list[Path]]:
    """Build forward dependency map using text scanning."""
    forward: dict[Path, list[Path]] = {}
    for path in files:
        includes = scan_includes_from_file(path)
        resolved: list[Path] = []
        for include in includes:
            candidates = resolve_include(include, files)
            if len(candidates) > 1:
                logger.warning("Ambiguous include '{}' in {}", include, path)
                continue
            if candidates:
                resolved.append(candidates[0])
        forward[path] = sorted(set(resolved))
    return forward
