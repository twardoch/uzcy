"""Path utilities for consistent output."""

from __future__ import annotations

from pathlib import Path


def abs_path(path: Path) -> Path:
    """Return an absolute, resolved path."""
    return path.expanduser().resolve()


def relative_posix(path: Path, root: Path) -> str:
    """Return POSIX path relative to root when possible."""
    try:
        return abs_path(path).relative_to(abs_path(root)).as_posix()
    except ValueError:
        return abs_path(path).as_posix()
