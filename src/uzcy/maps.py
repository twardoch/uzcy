# this_file: src/uzcy/maps.py
"""Dependency map helpers.

A *forward* map answers "what does this file include?"; the *reverse* map
(what `used_by` blocks show) answers "who includes this file?". The reverse map
is just the forward map with its edges flipped.
"""

from __future__ import annotations

from pathlib import Path

from uzcy.paths import abs_path


def _file_lookup(files: list[Path]) -> dict[Path, Path]:
    return {abs_path(path): path for path in files}


def build_forward_from_clang(
    raw_map: dict[str, list[str]],
    files: list[Path],
) -> dict[Path, list[Path]]:
    """Normalize clang output to a forward map limited to known files."""
    lookup = _file_lookup(files)
    forward: dict[Path, list[Path]] = {}
    for input_path, deps in raw_map.items():
        resolved = abs_path(Path(input_path))
        if resolved not in lookup:
            continue
        dep_paths: list[Path] = []
        for dep in deps:
            dep_resolved = abs_path(Path(dep))
            if dep_resolved in lookup:
                dep_paths.append(lookup[dep_resolved])
        forward[lookup[resolved]] = sorted(set(dep_paths))
    return forward


def invert_forward_map(forward: dict[Path, list[Path]]) -> dict[Path, list[Path]]:
    """Invert a forward dep map to file -> used_by list."""
    reverse: dict[Path, list[Path]] = {path: [] for path in forward}
    for user, deps in forward.items():
        for dep in deps:
            reverse.setdefault(dep, []).append(user)
    for key, values in reverse.items():
        reverse[key] = sorted(set(values))
    return reverse
