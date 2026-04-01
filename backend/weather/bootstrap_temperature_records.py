from __future__ import annotations

from collections.abc import Callable

from django.conf import settings

from weather.services.temperature_records.protocols import (
    TemperatureRecordsDataSource,
)


def _default_builder() -> TemperatureRecordsDataSource:
    from weather.data_sources.temperature_records_fake import (
        FakeTemperatureRecordsDataSource,
    )
    from weather.data_sources.timescale import HybridTemperatureRecordsDataSource

    if settings.MOCKED_DATA:
        return FakeTemperatureRecordsDataSource()
    return HybridTemperatureRecordsDataSource()


class TemperatureRecordsDependencyProvider:
    _builder: Callable[[], TemperatureRecordsDataSource] = _default_builder

    @classmethod
    def set_builder(cls, builder: Callable[[], TemperatureRecordsDataSource]) -> None:
        cls._builder = builder

    @classmethod
    def get_dep(cls) -> TemperatureRecordsDataSource:
        return cls._builder()

    @classmethod
    def reset(cls) -> None:
        cls._builder = _default_builder
