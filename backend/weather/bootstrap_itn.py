from collections.abc import Callable

from weather.data_sources.timescale import TimescaleNationalIndicatorDailyDataSource
from weather.services.national_indicator.protocols import (
    NationalIndicatorDailyDataSource,
)


class ITNDependencyProvider:
    """
    Point unique de câblage de la datasource ITN.
    """

    _builder: Callable[[], NationalIndicatorDailyDataSource] = (
        TimescaleNationalIndicatorDailyDataSource
    )

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
        cls._builder = TimescaleNationalIndicatorDailyDataSource
