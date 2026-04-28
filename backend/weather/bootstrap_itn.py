from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from django.conf import settings

from weather.services.national_indicator.protocols import (
    NationalIndicatorBaselineDataSource,
    NationalIndicatorObservedDataSource,
)


@dataclass(frozen=True)
class ITNDependencies:
    observed_data_source: NationalIndicatorObservedDataSource
    baseline_data_source: NationalIndicatorBaselineDataSource


def _default_builder() -> ITNDependencies:
    from weather.data_sources.national_indicator_fake import (
        FakeNationalIndicatorDataSource,
    )
    from weather.data_sources.timescale import (
        TimescaleNationalIndicatorBaselineDataSource,
        TimescaleNationalIndicatorObservedDataSource,
    )

    if settings.MOCKED_DATA:
        fake = FakeNationalIndicatorDataSource()
        return ITNDependencies(
            observed_data_source=fake,
            baseline_data_source=fake,
        )

    return ITNDependencies(
        observed_data_source=TimescaleNationalIndicatorObservedDataSource(),
        baseline_data_source=TimescaleNationalIndicatorBaselineDataSource(),
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
