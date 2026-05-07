from __future__ import annotations

from collections.abc import Callable

from django.conf import settings

from weather.services.temperature_extremes.protocols import (
    ExtremesGraphDataSource,
    ExtremesOverviewDataSource,
)


def _default_builder() -> ExtremesGraphDataSource:
    from weather.data_sources.temperature_extremes_fake import (
        FakeTemperatureExtremesDataSource,
    )
    from weather.data_sources.timescale import TimescaleTemperatureExtremesDataSource

    if settings.MOCKED_DATA:
        return FakeTemperatureExtremesDataSource()
    return TimescaleTemperatureExtremesDataSource()


def _default_overview_builder() -> ExtremesOverviewDataSource:
    from weather.data_sources.temperature_extremes_fake import (
        FakeTemperatureExtremesOverviewDataSource,
    )
    from weather.data_sources.timescale import (
        TimescaleTemperatureExtremesOverviewDataSource,
    )

    if settings.MOCKED_DATA:
        return FakeTemperatureExtremesOverviewDataSource()
    return TimescaleTemperatureExtremesOverviewDataSource()


class TemperatureExtremesDependencyProvider:
    _builder: Callable[[], ExtremesGraphDataSource] = _default_builder

    @classmethod
    def set_builder(cls, builder: Callable[[], ExtremesGraphDataSource]) -> None:
        cls._builder = builder

    @classmethod
    def get_dep(cls) -> ExtremesGraphDataSource:
        return cls._builder()

    @classmethod
    def reset(cls) -> None:
        cls._builder = _default_builder


class TemperatureExtremesOverviewDependencyProvider:
    _builder: Callable[[], ExtremesOverviewDataSource] = _default_overview_builder

    @classmethod
    def set_builder(cls, builder: Callable[[], ExtremesOverviewDataSource]) -> None:
        cls._builder = builder

    @classmethod
    def get_dep(cls) -> ExtremesOverviewDataSource:
        return cls._builder()

    @classmethod
    def reset(cls) -> None:
        cls._builder = _default_overview_builder
