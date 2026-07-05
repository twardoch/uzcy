# WORK

## Iteration 2 — Modernization for v1.0.0 (2026-07-05)

Scope: bring uzcy to portfolio release standard.

Done:
- hatch-vcs dynamic versioning; added the missing `[build-system]` table.
- `py.typed` + strict mypy (clean) + expanded ruff (clean).
- `pytest-cov`: 72 tests pass, 94% coverage.
- CI (`ci.yml`) and release (`release.yml`) workflows.
- `.gitignore` hygiene; Jekyll (Just the Docs) site under `docs/`.
- `this_file:` headers + backend-tradeoff comments across sources.
- `CLAUDE.md`, `AGENTS.md`; README clarifies uzcy is a sibling of uzpy, not a
  Cython port.

Verified: `uv build` produces sdist + wheel with a git-derived version; CLI
smoke run against `examples/simple` works.

## Iteration 1
Scope: Add initial tests, docs, and an example-based functional check for the existing uzcy implementation.

Plan:
- Add unit tests covering every function in `uzcy`.
- Add a functional test that runs the CLI against example fixtures.
- Create minimal project docs and a `test.sh` runner.
- Run tests and record results here.

Results:
- Tests: `./test.sh` (ruff check/format, pytest: 72 passed).
- Notes: fixed default exclude handling when `--exclude` is omitted; added docs, tests, examples, and test runner.

Wait, but...
- Double-checked that `--exclude ""` still disables excludes; kept behavior while restoring defaults.
