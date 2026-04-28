from __future__ import annotations

from collections.abc import Callable

from django.conf import settings

from weather.services.temperature_minmax.protocols import MinMaxGraphDataSource


def _default_builder() -> MinMaxGraphDataSource:
    from weather.data_sources.temperature_minmax_fake import (
        FakeTemperatureMinMaxDataSource,
    )
    from weather.data_sources.timescale import TimescaleTemperatureMinMaxDataSource

    if settings.MOCKED_DATA:
        return FakeTemperatureMinMaxDataSource()
    return TimescaleTemperatureMinMaxDataSource()


class TemperatureMinMaxDependencyProvider:
    _builder: Callable[[], MinMaxGraphDataSource] = _default_builder

    @classmethod
    def set_builder(cls, builder: Callable[[], MinMaxGraphDataSource]) -> None:
        cls._builder = builder

    @classmethod
    def get_dep(cls) -> MinMaxGraphDataSource:
        return cls._builder()

    @classmethod
    def reset(cls) -> None:
        cls._builder = _default_builder
