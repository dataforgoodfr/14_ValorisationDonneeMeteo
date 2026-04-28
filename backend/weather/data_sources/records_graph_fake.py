from __future__ import annotations

from weather.data_sources.temperature_records_fake import (
    _FAKE_COLD_RECORDS,
    _FAKE_HOT_RECORDS,
)
from weather.data_sources.timescale import _generate_buckets
from weather.regions import departments_for_region
from weather.services.records_graph.types import (
    RecordsGraphBucket,
    RecordsGraphRecord,
    RecordsGraphRequest,
    RecordsGraphResult,
)


class FakeRecordsGraphDataSource:
    """
    Data source fake pour le graphe de records.
    Agrège les fake records par bucket temporel.
    """

    def fetch_graph(self, request: RecordsGraphRequest) -> RecordsGraphResult:
        if request.type_records == "all":
            hot_base = list(_FAKE_HOT_RECORDS)
            cold_base = list(_FAKE_COLD_RECORDS)
        elif request.type_records == "hot":
            hot_base = list(_FAKE_HOT_RECORDS)
            cold_base = []
        else:
            hot_base = []
            cold_base = list(_FAKE_COLD_RECORDS)

        base = hot_base + cold_base

        entries = [
            e for e in base if request.date_start <= e.record_date <= request.date_end
        ]

        if request.territoire == "department":
            entries = [e for e in entries if e.department == request.territoire_id]
        elif request.territoire == "station":
            entries = [e for e in entries if e.station_id == request.territoire_id]
        elif request.territoire == "region":
            depts = set(departments_for_region(request.territoire_id or ""))
            entries = [e for e in entries if e.department in depts]

        counts: dict[str, int] = {}
        for e in entries:
            if request.granularity == "day":
                key = e.record_date.strftime("%Y-%m-%d")
            elif request.granularity == "month":
                key = e.record_date.strftime("%Y-%m")
            else:
                key = str(e.record_date.year)
            counts[key] = counts.get(key, 0) + 1

        all_buckets = _generate_buckets(
            request.date_start, request.date_end, request.granularity
        )
        buckets = [
            RecordsGraphBucket(bucket=b, nb_records_battus=counts.get(b, 0))
            for b in all_buckets
        ]

        hot_ids = {id(e) for e in hot_base}
        records = [
            RecordsGraphRecord(
                date=e.record_date,
                station_id=e.station_id,
                station_name=e.station_name,
                type_records="hot" if id(e) in hot_ids else "cold",
                valeur=e.record_value,
            )
            for e in entries
        ]
        return RecordsGraphResult(buckets=buckets, records=records)
