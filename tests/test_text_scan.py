from __future__ import annotations

from pathlib import Path

from uzcy.text_scan import (
    _strip_block_comment,
    _strip_line_comment,
    build_text_forward_map,
    resolve_include,
    scan_includes,
    scan_includes_from_file,
)


def test_strip_block_comment_when_in_block_then_returns_after_end() -> None:
    line, in_block = _strip_block_comment("end */ #include <a.h>", True)
    assert line.strip() == "#include <a.h>", "Should return text after block comment end"
    assert not in_block, "Should clear block state after end marker"


def test_strip_block_comment_when_no_end_then_returns_empty() -> None:
    line, in_block = _strip_block_comment("still in comment", True)
    assert line == "", "Should remove content while in block comment"
    assert in_block, "Should stay in block comment state"


def test_strip_line_comment_when_present_then_returns_prefix() -> None:
    cleaned = _strip_line_comment("#include <a.h> // trailing")
    assert cleaned.strip() == "#include <a.h>", "Should strip line comments"


def test_scan_includes_when_comments_then_ignores() -> None:
    text = """
// #include "ignored.h"
#include "a.h" // ok
/* #include "ignored2.h" */
/*
#include "ignored3.h"
*/
#include <b.h>
"""
    includes = scan_includes(text)
    assert includes == ["a.h", "b.h"], "Should only return real includes"


def test_scan_includes_when_empty_then_returns_empty() -> None:
    includes = scan_includes("")
    assert includes == [], "Empty input should return no includes"


def test_scan_includes_from_file_when_file_then_reads(tmp_path: Path) -> None:
    path = tmp_path / "main.c"
    path.write_text('#include "a.h"\n', encoding="utf-8")
    includes = scan_includes_from_file(path)
    assert includes == ["a.h"], "Should read file and return includes"


def test_resolve_include_when_suffix_matches_then_returns_match(tmp_path: Path) -> None:
    file_path = tmp_path / "inc" / "a.h"
    file_path.parent.mkdir()
    file_path.write_text("", encoding="utf-8")
    resolved = resolve_include("inc/a.h", [file_path])
    assert resolved == [file_path], "Should resolve by suffix match"


def test_resolve_include_when_basename_matches_then_returns_match(tmp_path: Path) -> None:
    file_path = tmp_path / "inc" / "a.h"
    file_path.parent.mkdir()
    file_path.write_text("", encoding="utf-8")
    resolved = resolve_include("a.h", [file_path])
    assert resolved == [file_path], "Should resolve by basename when no suffix match"


def test_build_text_forward_map_when_ambiguous_then_skips(tmp_path: Path) -> None:
    root = tmp_path
    (root / "a").mkdir()
    (root / "b").mkdir()
    (root / "main.c").write_text('#include "common.h"\n', encoding="utf-8")
    (root / "a" / "common.h").write_text("", encoding="utf-8")
    (root / "b" / "common.h").write_text("", encoding="utf-8")
    files = [root / "main.c", root / "a" / "common.h", root / "b" / "common.h"]
    forward = build_text_forward_map(files)
    assert forward[root / "main.c"] == [], "Ambiguous includes should be skipped"
