"""Configuration models and defaults."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field, field_validator

DEFAULT_EXCLUDES = [
    ".git",
    "build",
    "out",
    ".cache",
    ".venv",
]

C_EXTENSIONS = [
    ".c",
    ".cc",
    ".cpp",
    ".cxx",
    ".h",
    ".hh",
    ".hpp",
    ".hxx",
]


class UzcyConfig(BaseModel):
    """Runtime configuration for uzcy."""

    path: Path = Field(default_factory=Path.cwd)
    compile_db: Path | None = None
    mode: str = "auto"
    exclude: list[str] = Field(default_factory=lambda: DEFAULT_EXCLUDES.copy())
    dry_run: bool = False
    backup: Path | None = None
    verbose: bool = False

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, value: str) -> str:
        valid = {"auto", "clang", "text"}
        if value not in valid:
            raise ValueError(f"mode must be one of {sorted(valid)}")
        return value
