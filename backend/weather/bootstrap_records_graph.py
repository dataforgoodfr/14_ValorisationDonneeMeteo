from __future__ import annotations

from collections.abc import Callable

from django.conf import settings

from weather.services.records_graph.protocols import RecordsGraphDataSource


def _default_builder() -> RecordsGraphDataSource:
    from weather.data_sources.records_graph_fake import FakeRecordsGraphDataSource
    from weather.data_sources.timescale import TimescaleRecordsGraphDataSource

    if settings.MOCKED_DATA:
        return FakeRecordsGraphDataSource()
    return TimescaleRecordsGraphDataSource()


class RecordsGraphDependencyProvider:
    _builder: Callable[[], RecordsGraphDataSource] = _default_builder

    @classmethod
    def set_builder(cls, builder: Callable[[], RecordsGraphDataSource]) -> None:
        cls._builder = builder

    @classmethod
    def get_dep(cls) -> RecordsGraphDataSource:
        return cls._builder()

    @classmethod
    def reset(cls) -> None:
        cls._builder = _default_builder
