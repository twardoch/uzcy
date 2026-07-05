# PLAN

## Status

The v1.0.0 modernization pass is complete: hatch-vcs versioning, strict typing,
CI + release workflows, Jekyll docs, and clarified positioning against uzpy.
See `CHANGELOG.md` for the shipped items.

## Next phase (post-1.0)

Future work is tracked in `TODO.md`. The themes:

1. **Ergonomics** — project-level config file; a `--check` CI mode that fails on
   stale blocks without writing.
2. **Text-backend accuracy** — surface a skipped-ambiguous-include summary;
   decide how to treat macro/computed include paths.
3. **Test depth** — a clang-backend integration test against a fixture
   `compile_commands.json`, skipped when the toolchain is absent.
4. **Portfolio integration** — a shared "used_by" concept doc linking uzpy and
   uzcy so users understand the pair.
