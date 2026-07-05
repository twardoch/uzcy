---
title: Backends
layout: default
nav_order: 2
---

# Backends: clang vs. text

`uzcy` resolves includes two ways. They answer the same question with different
precision.

## clang backend

Drives `clang-scan-deps` over a `compile_commands.json`. The real preprocessor
resolves every include exactly as the compiler sees it — the same header search
paths, the same conditional compilation. This is the accurate answer.

It needs two things:

- `clang-scan-deps` on your `PATH` (ships with LLVM/Clang).
- A `compile_commands.json` describing how each file is built. See
  [compile_commands.json setup](setup.md).

## text backend

Reads `#include` lines directly. No compiler, no compile database — it runs on
any tree. The cost is precision:

- It matches an include to a file by path suffix, then by basename.
- If an include name matches more than one file in the tree, it is **skipped**
  (and logged under `--verbose`) rather than guessed.
- Commented-out includes — line and block comments — are ignored.
- Preprocessor conditionals are not evaluated, so an include inside a disabled
  `#if` still counts.

## auto mode (default)

`--mode auto` prefers the clang backend when a compile database is found, and
falls back to the text scanner otherwise. If the clang run errors, `uzcy` logs
the failure and still completes with the text backend — a missing compiler
never fails the run.

Force one with `--mode clang` (errors if no compile database) or `--mode text`.

| | clang | text |
|---|---|---|
| Needs `compile_commands.json` | yes | no |
| Needs `clang-scan-deps` | yes | no |
| Honors header search paths | yes | no |
| Honors `#if` conditionals | yes | no |
| Runs anywhere | no | yes |
