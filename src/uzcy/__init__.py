# this_file: src/uzcy/__init__.py
"""uzcy: reverse include dependency tracker for C/C++."""

from __future__ import annotations

try:
    from uzcy.__version__ import __version__
except ImportError:  # pragma: no cover - source checkout without a build
    __version__ = "0.0.0.dev0"

__all__ = ["__version__"]
