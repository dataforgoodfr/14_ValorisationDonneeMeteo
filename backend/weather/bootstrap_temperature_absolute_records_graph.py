from __future__ import annotations

import datetime as dt
from collections.abc import Callable

from django.conf import settings

from weather.data_sources.records_graph_fake import FakeAbsoluteRecordsGraphDataSource
from weather.data_sources.timescale import TimescaleAbsoluteRecordsGraphDataSource
from weather.services.records_graph.protocols import AbsoluteRecordsGraphDataSource
from weather.services.records_graph.types import (
    AbsoluteRecordsGraphBucket,
    AbsoluteRecordsGraphResult,
    RecordsGraphRecord,
)

_MOCKED_RESULT = AbsoluteRecordsGraphResult(
    buckets=[
        AbsoluteRecordsGraphBucket(bucket="2019", nb_records_absolus=2),
        AbsoluteRecordsGraphBucket(bucket="2020", nb_records_absolus=1),
        AbsoluteRecordsGraphBucket(bucket="2021", nb_records_absolus=3),
        AbsoluteRecordsGraphBucket(bucket="2022", nb_records_absolus=4),
        AbsoluteRecordsGraphBucket(bucket="2023", nb_records_absolus=2),
    ],
    records=[
        RecordsGraphRecord(
            date=dt.date(2019, 7, 25),
            station_id="94003001",
            station_name="ORLY",
            department="94",
            type_records="hot",
            valeur=42.0,
        ),
        RecordsGraphRecord(
            date=dt.date(2020, 8, 11),
            station_id="76116000",
            station_name="ROUEN",
            department="76",
            type_records="hot",
            valeur=40.5,
        ),
    ],
)


def _default_builder() -> AbsoluteRecordsGraphDataSource:
    if settings.MOCKED_DATA:
        return FakeAbsoluteRecordsGraphDataSource(_MOCKED_RESULT)
    return TimescaleAbsoluteRecordsGraphDataSource()


class TemperatureAbsoluteRecordsGraphDependencyProvider:
    _builder: Callable[[], AbsoluteRecordsGraphDataSource] = _default_builder

    @classmethod
    def set_builder(cls, builder: Callable[[], AbsoluteRecordsGraphDataSource]) -> None:
        cls._builder = builder

    @classmethod
    def get_dep(cls) -> AbsoluteRecordsGraphDataSource:
        return cls._builder()

    @classmethod
    def reset(cls) -> None:
        cls._builder = _default_builder
