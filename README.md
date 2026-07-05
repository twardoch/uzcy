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

Add `--dry-run` to preview without touching any file.

## Definition

A file is listed under `used_by` when another file **directly includes** it.
There is no transitive analysis: if `a.c` includes `b.h` and `b.h` includes
`c.h`, then `c.h` lists `b.h`, not `a.c`.

## Requirements

- Python 3.12+
- Optional: `clang-scan-deps` for the clang backend (recommended when `compile_commands.json` exists)

## Install (dev)

```bash
cd uzcy
uv venv
source .venv/bin/activate
uv pip install -e ".[dev,test]"
```

## Usage

```bash
uzcy run --path .
```

Key flags:

- `--mode auto|clang|text` (default: auto)
- `--compile-db path/to/compile_commands.json`
- `--exclude ".git,build,out"` (empty string disables excludes)
- `--dry-run`
- `--backup path/to/backup`
- `--verbose`

## Output format

```
// <used_by>
// - path/to/user.cpp
// - path/to/user.h
// </used_by>
```

## Notes

- In `auto` mode, `clang-scan-deps` is used when a compile database is found; otherwise it falls back to a text scan.
- The text scanner ignores commented `#include` lines and skips ambiguous includes when multiple files match.
- Writes are atomic and idempotent: a run with no dependency change leaves files byte-for-byte identical, preserving line endings.

## Visual

![uzcy icon](docs/assets/icon.png)

## Documentation

Full docs at [twardoch.github.io/uzcy](https://twardoch.github.io/uzcy/):
backend comparison, `compile_commands.json` setup, and the `// <used_by>` block
format spec.

## Relationship to uzpy

`uzcy` is the C/C++ sibling of [`uzpy`](https://github.com/twardoch/uzpy). They
share one idea — annotate code with where it is used — but are separate tools
with separate codebases. `uzpy` reads Python and writes "Used in:" docstring
sections; `uzcy` reads C/C++ `#include` graphs and writes `// <used_by>` comment
blocks. `uzcy` is not a Cython or compiled port of `uzpy`.

## License

MIT — see the package metadata.
