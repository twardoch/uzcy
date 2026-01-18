# Dependencies

## Runtime

- `fire`: minimal CLI wiring.
- `rich`: readable console output.
- `loguru`: simple logging with `--verbose` toggle.
- `pydantic`: config validation with clear errors.

## Dev

- `pytest`: tests.
- `ruff`: lint + format.

## External tools

- `clang-scan-deps` (optional): accurate include graph when `compile_commands.json` is present.

## Decision notes

- Prefer `clang-scan-deps` for accuracy when a compile database exists; fall back to text scanning to keep the tool usable without it.
