from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from django.conf import settings

from weather.services.national_indicator.protocols import (
    NationalIndicatorAbsoluteExtremesDataSource,
    NationalIndicatorBaselineDataSource,
    NationalIndicatorKpiDataSource,
    NationalIndicatorObservedDataSource,
)


@dataclass(frozen=True)
class ITNDependencies:
    observed_data_source: NationalIndicatorObservedDataSource
    baseline_data_source: NationalIndicatorBaselineDataSource
    absolute_extremes_data_source: NationalIndicatorAbsoluteExtremesDataSource
    kpi_data_source: NationalIndicatorKpiDataSource


def _default_builder() -> ITNDependencies:
    from weather.data_sources.national_indicator_fake import (
        FakeNationalIndicatorAbsoluteExtremesDataSource,
        FakeNationalIndicatorDataSource,
        FakeNationalIndicatorKpiDataSource,
    )
    from weather.data_sources.timescale import (
        TimescaleNationalIndicatorAbsoluteExtremesDataSource,
        TimescaleNationalIndicatorBaselineDataSource,
        TimescaleNationalIndicatorKpiDataSource,
        TimescaleNationalIndicatorObservedDataSource,
    )

    if settings.MOCKED_DATA:
        fake = FakeNationalIndicatorDataSource()
        return ITNDependencies(
            observed_data_source=fake,
            baseline_data_source=fake,
            absolute_extremes_data_source=FakeNationalIndicatorAbsoluteExtremesDataSource(),
            kpi_data_source=FakeNationalIndicatorKpiDataSource(fake=fake),
        )

    return ITNDependencies(
        observed_data_source=TimescaleNationalIndicatorObservedDataSource(),
        baseline_data_source=TimescaleNationalIndicatorBaselineDataSource(),
        absolute_extremes_data_source=TimescaleNationalIndicatorAbsoluteExtremesDataSource(),
        kpi_data_source=TimescaleNationalIndicatorKpiDataSource(),
    )


class ITNDependencyProvider:
    _builder: Callable[[], ITNDependencies] = _default_builder

    @classmethod
    def set_builder(cls, builder: Callable[[], ITNDependencies]) -> None:
        cls._builder = builder

    @classmethod
    def get_dep(cls) -> ITNDependencies:
        return cls._builder()

    @classmethod
    def reset(cls) -> None:
        cls._builder = _default_builder
