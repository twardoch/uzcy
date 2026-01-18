#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")" && pwd)
cd "$ROOT"

uv run --extra dev ruff check --fix .
uv run --extra dev ruff format .
uv run --extra dev pytest -xvs
