from __future__ import annotations

import pytest

from uzcy.config import DEFAULT_EXCLUDES, UzcyConfig


def test_uzcy_config_when_default_then_has_default_excludes() -> None:
    config = UzcyConfig()
    assert config.exclude == DEFAULT_EXCLUDES, "Default excludes should be set"


def test_uzcy_config_when_invalid_mode_then_raises() -> None:
    with pytest.raises(ValueError, match="mode must be one of"):
        UzcyConfig(mode="bad")
