"""Unit tests for configuration loader."""
from __future__ import annotations

from collections.abc import Generator

import pytest

from src.app.core import config


@pytest.fixture(autouse=True)
def reset_settings_cache() -> Generator[None, None, None]:
    config.get_settings.cache_clear()
    yield
    config.get_settings.cache_clear()


def test_settings_reads_environment_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("API_PORT", "9001")
    settings = config.get_settings()

    assert settings.api_port == 9001


def test_feature_flags_default_enabled() -> None:
    settings = config.get_settings()

    assert settings.feature_flags.knowledge_workers_enabled is True
    assert settings.feature_flags.recommendation_caching_enabled is True


def test_settings_can_be_reloaded_with_new_values(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = config.get_settings()
    assert settings.log_level == "INFO"

    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    config.get_settings.cache_clear()
    updated = config.get_settings()

    assert updated.log_level == "DEBUG"
