# TODO

Low-hanging fruit and future ideas for uzcy. Nothing here blocks the release.

- [ ] Add a `pyproject.toml`-driven config file so per-project excludes and mode
      need not be passed on every invocation.
- [ ] Emit a summary of skipped ambiguous includes (count + names) at the end of
      a text-backend run, not just per-line `--verbose` warnings.
- [ ] Support a `--check` mode that exits non-zero when any block is stale (for
      CI use), without writing.
- [ ] Handle `#include` with computed/macro paths gracefully in the text backend
      (currently silently ignored).
- [ ] Add an integration test that exercises the clang backend against a small
      fixture `compile_commands.json` (skipped when `clang-scan-deps` absent).
- [ ] Consider a shared "used_by" framing doc cross-linking uzpy and uzcy.
