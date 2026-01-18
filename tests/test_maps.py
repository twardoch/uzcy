from __future__ import annotations

from pathlib import Path

from uzcy.maps import _file_lookup, build_forward_from_clang, invert_forward_map


def test_file_lookup_when_paths_then_returns_abs_mapping(tmp_path: Path) -> None:
    path = tmp_path / "main.c"
    lookup = _file_lookup([path])
    assert path.resolve() in lookup, "Lookup should be keyed by absolute paths"
    assert lookup[path.resolve()] == path, "Lookup should map to original path object"


def test_build_forward_from_clang_when_known_files_then_filters(tmp_path: Path) -> None:
    root = tmp_path
    main = root / "main.c"
    header = root / "a.h"
    raw = {
        str(main): [str(header), str(root / "missing.h")],
        str(root / "other.c"): [str(header)],
    }
    forward = build_forward_from_clang(raw, [main, header])
    assert forward == {main: [header]}, "Should only include dependencies in known file set"


def test_invert_forward_map_when_deps_then_reverse_sorted(tmp_path: Path) -> None:
    a = tmp_path / "a.h"
    b = tmp_path / "b.c"
    c = tmp_path / "c.c"
    forward = {b: [a], c: [a]}
    reverse = invert_forward_map(forward)
    assert reverse[a] == [b, c], "Reverse map should be sorted and deduped"
