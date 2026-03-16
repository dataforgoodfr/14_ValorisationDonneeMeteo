from __future__ import annotations

from collections.abc import Callable

from django.conf import settings

from weather.services.national_indicator.protocols import (
    NationalIndicatorDailyDataSource,
)


def _default_builder() -> NationalIndicatorDailyDataSource:
    from weather.data_sources.national_indicator_fake import (
        FakeNationalIndicatorDailyDataSource,
    )
    from weather.data_sources.timescale import TimescaleNationalIndicatorDailyDataSource

    if settings.MOCKED_DATA:
        return FakeNationalIndicatorDailyDataSource()
    return TimescaleNationalIndicatorDailyDataSource()


class ITNDependencyProvider:
    _builder: Callable[[], NationalIndicatorDailyDataSource] = _default_builder

    @classmethod
    def set_builder(
        cls, builder: Callable[[], NationalIndicatorDailyDataSource]
    ) -> None:
        cls._builder = builder

    @classmethod
    def get_dep(cls) -> NationalIndicatorDailyDataSource:
        return cls._builder()

    @classmethod
    def reset(cls) -> None:
        cls._builder = _default_builder
