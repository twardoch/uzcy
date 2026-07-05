# this_file: src/uzcy/cli.py
"""CLI entrypoint for uzcy."""

from __future__ import annotations

from pathlib import Path

import fire
from loguru import logger
from rich.console import Console

from uzcy.clang_backend import find_compile_db, parse_clang_scan_deps, run_clang_scan_deps
from uzcy.config import C_EXTENSIONS, DEFAULT_EXCLUDES, UzcyConfig
from uzcy.discovery import discover_files
from uzcy.maps import build_forward_from_clang, invert_forward_map
from uzcy.paths import abs_path, relative_posix
from uzcy.text_scan import build_text_forward_map
from uzcy.writer import update_file

CONSOLE = Console()


def _setup_logging(verbose: bool) -> None:
    logger.remove()
    level = "DEBUG" if verbose else "INFO"
    logger.add(lambda msg: CONSOLE.print(msg, end=""), level=level)


def _parse_excludes(exclude: str | None) -> list[str]:
    if exclude is None:
        return DEFAULT_EXCLUDES.copy()
    if not exclude:
        return []
    return [item.strip() for item in exclude.split(",") if item.strip()]


def _resolve_compile_db(config: UzcyConfig, root: Path) -> Path | None:
    if config.compile_db:
        return abs_path(config.compile_db)
    return find_compile_db(root)


def _run_clang_backend(files: list[Path], compile_db: Path) -> dict[Path, list[Path]]:
    raw = run_clang_scan_deps(compile_db)
    parsed = parse_clang_scan_deps(raw)
    return build_forward_from_clang(parsed, files)


def _run_text_backend(files: list[Path]) -> dict[Path, list[Path]]:
    return build_text_forward_map(files)


def _select_forward_map(
    config: UzcyConfig, files: list[Path], root: Path
) -> dict[Path, list[Path]]:
    compile_db = _resolve_compile_db(config, root)
    if config.mode == "text":
        return _run_text_backend(files)
    if config.mode == "clang":
        if not compile_db:
            raise FileNotFoundError("compile_commands.json not found")
        return _run_clang_backend(files, compile_db)
    # auto mode: prefer the accurate clang backend when a compile database is
    # present, but never fail the run over it -- drop to the text scanner if
    # clang is missing or errors out.
    if compile_db:
        try:
            return _run_clang_backend(files, compile_db)
        except Exception as exc:  # pragma: no cover - log and fallback
            logger.warning("clang backend failed: {}", exc)
    return _run_text_backend(files)


def _format_used_by(used_by: list[Path], root: Path) -> list[str]:
    return [relative_posix(path, root) for path in used_by]


def _build_config(
    path: str,
    compile_db: str | None,
    mode: str,
    exclude: str | None,
    dry_run: bool,
    backup: str | None,
    verbose: bool,
) -> UzcyConfig:
    return UzcyConfig(
        path=Path(path),
        compile_db=Path(compile_db) if compile_db else None,
        mode=mode,
        exclude=_parse_excludes(exclude),
        dry_run=dry_run,
        backup=Path(backup) if backup else None,
        verbose=verbose,
    )


def _run_with_config(config: UzcyConfig) -> None:
    _setup_logging(config.verbose)
    root = abs_path(config.path)
    files = discover_files(root, config.exclude, C_EXTENSIONS)
    if not files:
        CONSOLE.print("No C/C++ files found.")
        return
    forward = _select_forward_map(config, files, root)
    reverse = invert_forward_map(forward)
    updated = 0
    for path in files:
        used_by = _format_used_by(reverse.get(path, []), root)
        if update_file(path, used_by, config.dry_run, config.backup, root):
            updated += 1
    CONSOLE.print(f"Scanned {len(files)} files; updated {updated}; skipped {len(files) - updated}.")


def run(
    path: str = ".",
    compile_db: str | None = None,
    mode: str = "auto",
    exclude: str | None = None,
    dry_run: bool = False,
    backup: str | None = None,
    verbose: bool = False,
) -> None:
    """Compute reverse include deps and update used_by blocks."""
    config = _build_config(path, compile_db, mode, exclude, dry_run, backup, verbose)
    _run_with_config(config)


def main() -> None:
    fire.Fire({"run": run})


if __name__ == "__main__":
    main()
