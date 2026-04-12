from __future__ import annotations

from collections.abc import Callable

from django.conf import settings

from weather.services.records.protocols import RecordsDataSource


def _default_builder() -> RecordsDataSource:
    from weather.data_sources.records_fake import FakeRecordsDataSource
    from weather.data_sources.timescale import TimescaleRecordsDataSource

    if settings.MOCKED_DATA:
        return FakeRecordsDataSource()
    return TimescaleRecordsDataSource()


class RecordsDependencyProvider:
    _builder: Callable[[], RecordsDataSource] = _default_builder

    @classmethod
    def set_builder(cls, builder: Callable[[], RecordsDataSource]) -> None:
        cls._builder = builder

    @classmethod
    def get_dep(cls) -> RecordsDataSource:
        return cls._builder()

    @classmethod
    def reset(cls) -> None:
        cls._builder = _default_builder
