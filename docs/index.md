---
title: Home
layout: default
nav_order: 1
---

# uzcy

A header file that knows who includes it.

`uzcy` scans a C/C++ tree, works out which files include which, and writes a
`// <used_by>` comment block into each included file listing the files that pull
it in. Run it again after refactoring and the blocks update in place.

## Install

```bash
uv pip install uzcy
```

## Quick start

```bash
uzcy run --path .
```

That walks the current directory, computes reverse-include dependencies, and
updates every `// <used_by>` block. Add `--dry-run` to preview without writing.

## What a block looks like

A file gets one block near the top:

```c
// <used_by>
// - src/app.c
// - src/render.c
// </used_by>
```

A file is listed under `used_by` when another file **directly** includes it.
There is no transitive analysis: if `a.c` includes `b.h` and `b.h` includes
`c.h`, then `c.h` lists `b.h`, not `a.c`.

## Key flags

| Flag | Meaning |
|---|---|
| `--mode auto\|clang\|text` | Backend selection (default `auto`) |
| `--compile-db PATH` | Point at a `compile_commands.json` |
| `--exclude ".git,build"` | Comma-separated dir/glob excludes (empty string disables) |
| `--dry-run` | Report changes without writing |
| `--backup PATH` | Copy originals into this directory before editing |
| `--verbose` | Debug logging |

## Next steps

- [Backends: clang vs. text](backends.md) — how the two scanners differ.
- [compile_commands.json setup](setup.md) — feeding the clang backend.
- [used_by block format](format.md) — the exact block contract.

## Relationship to uzpy

`uzcy` is the C/C++ sibling of [`uzpy`](https://github.com/twardoch/uzpy).
They share one idea — annotate code with where it is used — but are separate
tools with separate codebases. `uzpy` reads Python and writes "Used in:"
docstring sections; `uzcy` reads C/C++ `#include` graphs and writes `// <used_by>`
comment blocks. `uzcy` is not a Cython or compiled port of `uzpy`.
