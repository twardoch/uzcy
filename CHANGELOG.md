# Changelog

All notable changes to this project are documented here.

## Unreleased

### Modernization pass (2026-07-05)

- Switch to `hatch-vcs` dynamic versioning from git tags; add the missing
  `[build-system]` table (the project previously had none).
- Add `py.typed` marker and ship it in the wheel.
- Add strict `mypy` and expanded `ruff` lint config; fix all findings.
- Add `pytest-cov`; coverage now reported (94% at this pass).
- Add GitHub Actions: `ci.yml` (ruff + mypy + pytest on 3.12/3.13) and
  `release.yml` (build + publish to PyPI on `v*` tags).
- `.gitignore` hygiene: ignore build artifacts, caches, and the generated
  version file.
- Add Jekyll (Just the Docs) documentation site under `docs/`: backend
  comparison, `compile_commands.json` setup, and `// <used_by>` block spec.
- Add `this_file:` headers and explanatory comments across all source files.
- Add `CLAUDE.md` and `AGENTS.md`; clarify in README that `uzcy` is a sibling
  of `uzpy`, not a Cython port.

## Earlier

- Add initial test suite with unit and functional coverage.
- Add README, dependency notes, and work log.
- Fix default exclude handling when `--exclude` is not provided.
