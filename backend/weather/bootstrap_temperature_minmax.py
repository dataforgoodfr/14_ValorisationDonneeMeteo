from __future__ import annotations

from collections.abc import Callable

from django.conf import settings

from weather.services.temperature_minmax.protocols import (
    MinMaxGraphDataSource,
    MinMaxOverviewDataSource,
)


def _default_builder() -> MinMaxGraphDataSource:
    from weather.data_sources.temperature_minmax_fake import (
        FakeTemperatureMinMaxDataSource,
    )
    from weather.data_sources.timescale import TimescaleTemperatureMinMaxDataSource

    if settings.MOCKED_DATA:
        return FakeTemperatureMinMaxDataSource()
    return TimescaleTemperatureMinMaxDataSource()


def _default_overview_builder() -> MinMaxOverviewDataSource:
    from weather.data_sources.temperature_minmax_fake import (
        FakeTemperatureMinMaxOverviewDataSource,
    )
    from weather.data_sources.timescale import (
        TimescaleTemperatureMinMaxOverviewDataSource,
    )

    if settings.MOCKED_DATA:
        return FakeTemperatureMinMaxOverviewDataSource()
    return TimescaleTemperatureMinMaxOverviewDataSource()


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


class TemperatureMinMaxOverviewDependencyProvider:
    _builder: Callable[[], MinMaxOverviewDataSource] = _default_overview_builder

    @classmethod
    def set_builder(cls, builder: Callable[[], MinMaxOverviewDataSource]) -> None:
        cls._builder = builder

    @classmethod
    def get_dep(cls) -> MinMaxOverviewDataSource:
        return cls._builder()

    @classmethod
    def reset(cls) -> None:
        cls._builder = _default_overview_builder
