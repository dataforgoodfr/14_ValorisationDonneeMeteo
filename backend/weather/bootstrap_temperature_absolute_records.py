from __future__ import annotations

from collections.abc import Callable

from django.conf import settings

from weather.data_sources.timescale import TimescaleTemperatureAbsoluteRecordsDataSource
from weather.services.temperature_records.protocols import (
    TemperatureAbsoluteRecordsDataSource,
)


def _default_builder() -> TemperatureAbsoluteRecordsDataSource:
    from weather.data_sources.temperature_records_fake import (
        FakeTemperatureAbsoluteRecordsDataSource,
    )

    if settings.MOCKED_DATA:
        return FakeTemperatureAbsoluteRecordsDataSource()
    return TimescaleTemperatureAbsoluteRecordsDataSource()


class TemperatureAbsoluteRecordsDependencyProvider:
    _builder: Callable[[], TemperatureAbsoluteRecordsDataSource] = _default_builder

    @classmethod
    def set_builder(
        cls, builder: Callable[[], TemperatureAbsoluteRecordsDataSource]
    ) -> None:
        cls._builder = builder

    @classmethod
    def get_dep(cls) -> TemperatureAbsoluteRecordsDataSource:
        return cls._builder()

    @classmethod
    def reset(cls) -> None:
        cls._builder = _default_builder
