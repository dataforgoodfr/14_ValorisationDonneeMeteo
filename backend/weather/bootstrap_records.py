
from collections.abc import Callable

from weather.services.records.protocols import RecordsDataSource

def _default_builder() -> RecordsDataSource:
    from weather.data_sources.timescale import TimescaleRecordsDataSource

    return TimescaleRecordsDataSource()

class RecordsDependencyProvider:
    _builder: Callable[[], RecordsDataSource] = _default_builder

    @classmethod
    def set_builder(
        cls, builder: Callable[[], RecordsDataSource]
    ) -> None:
        cls._builder = builder

    @classmethod
    def get_dep(cls) -> RecordsDataSource:
        return cls._builder()

    @classmethod
    def reset(cls) -> None:
        cls._builder = _default_builder