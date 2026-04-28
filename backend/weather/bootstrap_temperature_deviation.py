from __future__ import annotations

from collections.abc import Callable

from django.conf import settings

from weather.services.temperature_deviation.protocols import (
    TemperatureDeviationDailyDataSource,
    TemperatureDeviationOverviewDataSource,
)

# =========================
# Builders
# =========================


def _default_daily_builder() -> TemperatureDeviationDailyDataSource:
    from weather.data_sources.temperature_deviation_fake import (
        FakeTemperatureDeviationDailyDataSource,
    )
    from weather.data_sources.timescale import (
        TimescaleTemperatureDeviationDailyDataSource,
    )

    if settings.MOCKED_DATA:
        return FakeTemperatureDeviationDailyDataSource()
    return TimescaleTemperatureDeviationDailyDataSource()


def _default_overview_builder() -> TemperatureDeviationOverviewDataSource:
    from weather.data_sources.temperature_deviation_fake import (
        FakeTemperatureDeviationOverviewDataSource,
    )
    from weather.data_sources.timescale import (
        TimescaleTemperatureDeviationDailyDataSource,
    )

    if settings.MOCKED_DATA:
        return FakeTemperatureDeviationOverviewDataSource()
    return TimescaleTemperatureDeviationDailyDataSource()


# =========================
# Providers
# =========================


class TemperatureDeviationDependencyProvider:
    _builder: Callable[[], TemperatureDeviationDailyDataSource] = _default_daily_builder

    @classmethod
    def set_builder(
        cls, builder: Callable[[], TemperatureDeviationDailyDataSource]
    ) -> None:
        cls._builder = builder

    @classmethod
    def get_dep(cls) -> TemperatureDeviationDailyDataSource:
        return cls._builder()

    @classmethod
    def reset(cls) -> None:
        cls._builder = _default_daily_builder


class TemperatureDeviationOverviewDependencyProvider:
    _builder: Callable[[], TemperatureDeviationOverviewDataSource] = (
        _default_overview_builder
    )

    @classmethod
    def set_builder(
        cls, builder: Callable[[], TemperatureDeviationOverviewDataSource]
    ) -> None:
        cls._builder = builder

    @classmethod
    def get_dep(cls) -> TemperatureDeviationOverviewDataSource:
        return cls._builder()

    @classmethod
    def reset(cls) -> None:
        cls._builder = _default_overview_builder
