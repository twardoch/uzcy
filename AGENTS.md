# AGENTS.md

See [CLAUDE.md](CLAUDE.md) for the layout, architecture notes, commands, and
gotchas. Same guidance applies to any coding agent working in this repo.

Quick contract: keep `ruff check`, `ruff format --check`, `mypy` (strict), and
`pytest` green before committing. Version comes from git tags via hatch-vcs —
never hand-edit `src/uzcy/__version__.py`.
