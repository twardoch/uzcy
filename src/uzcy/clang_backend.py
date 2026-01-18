"""clang-scan-deps integration."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


def find_compile_db(root: Path) -> Path | None:
    """Return the first compile_commands.json under root, if any."""
    direct = root / "compile_commands.json"
    if direct.exists():
        return direct
    for path in root.rglob("compile_commands.json"):
        return path
    return None


def _ensure_clang_scan_deps() -> str:
    tool = shutil.which("clang-scan-deps")
    if not tool:
        raise FileNotFoundError("clang-scan-deps not found on PATH")
    return tool


def run_clang_scan_deps(compile_db: Path) -> str:
    """Run clang-scan-deps and return stdout."""
    tool = _ensure_clang_scan_deps()
    cmd = [tool, "-format=json", "-compilation-database", str(compile_db)]
    result = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "clang-scan-deps failed")
    return result.stdout


def _decode_json_stream(raw: str) -> list[object]:
    decoder = json.JSONDecoder()
    items: list[object] = []
    index = 0
    raw = raw.strip()
    while index < len(raw):
        obj, next_index = decoder.raw_decode(raw, index)
        items.append(obj)
        index = next_index
        while index < len(raw) and raw[index].isspace():
            index += 1
    return items


def _load_json(raw: str) -> object:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return _decode_json_stream(raw)


def _normalize_entries(data: object) -> list[dict[str, object]]:
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        if "translation-units" in data:
            items = data.get("translation-units")
            return [item for item in items if isinstance(item, dict)]
        return [data]
    return []


def _extract_paths(values: object) -> list[str]:
    if not isinstance(values, list):
        return []
    paths: list[str] = []
    for value in values:
        if isinstance(value, str):
            paths.append(value)
        elif isinstance(value, dict):
            for key in ("file", "path"):
                if key in value and isinstance(value[key], str):
                    paths.append(value[key])
    return paths


def _pick_deps(entry: dict[str, object]) -> list[str]:
    for key in ("direct-deps", "direct-dependencies", "file-deps", "dependencies"):
        if key in entry:
            deps = _extract_paths(entry[key])
            if deps:
                return deps
    return []


def parse_clang_scan_deps(raw: str) -> dict[str, list[str]]:
    """Parse clang-scan-deps output into a forward dep map."""
    data = _load_json(raw)
    entries = _normalize_entries(data)
    output: dict[str, list[str]] = {}
    for entry in entries:
        input_file = entry.get("input-file") or entry.get("file") or entry.get("source")
        if not isinstance(input_file, str):
            continue
        deps = _pick_deps(entry)
        if deps:
            output[input_file] = deps
    return output
