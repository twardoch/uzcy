# this_file: src/uzcy/discovery.py
"""File discovery for C/C++ sources."""

from __future__ import annotations

import os
from pathlib import Path

from uzcy.paths import relative_posix


def is_excluded(path: Path, root: Path, patterns: list[str]) -> bool:
    """Return True when path matches any exclude pattern."""
    rel = relative_posix(path, root)
    parts = Path(rel).parts
    for pattern in patterns:
        if pattern in parts:
            return True
        if Path(rel).match(pattern):
            return True
    return False


def _filter_dirs(root: Path, dirpath: Path, dirnames: list[str], patterns: list[str]) -> None:
    keep: list[str] = []
    for name in dirnames:
        if not is_excluded(dirpath / name, root, patterns):
            keep.append(name)
    dirnames[:] = keep


def discover_files(root: Path, patterns: list[str], extensions: list[str]) -> list[Path]:
    """Recursively discover files by extension, applying excludes."""
    root = root.resolve()
    found: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirpath_path = Path(dirpath)
        _filter_dirs(root, dirpath_path, dirnames, patterns)
        for filename in filenames:
            file_path = dirpath_path / filename
            if file_path.suffix.lower() in extensions and not is_excluded(
                file_path, root, patterns
            ):
                found.append(file_path)
    return sorted(found)
