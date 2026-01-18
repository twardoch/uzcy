# uzcy

Reverse include dependency tracker for C/C++ that maintains `// <used_by>` blocks.

## Definition

A file is listed under `used_by` when it **directly includes** the file (no transitive analysis).

## Requirements

- Python 3.12+
- Optional: `clang-scan-deps` for the clang backend (recommended when `compile_commands.json` exists)

## Install (dev)

```bash
cd uzcy
uv venv
source .venv/bin/activate
uv pip install -e .
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
