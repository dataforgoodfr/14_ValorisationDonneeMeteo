from __future__ import annotations

import datetime as dt

from weather.services.temperature_records.types import (
    Pagination,
    TemperatureRecordEntry,
    TemperatureRecordsRequest,
    TemperatureRecordsResult,
)

# Données fake déterministes pour les records progressifs de température.
# Plusieurs lignes par station : chaque ligne est une fois où la station a
# battu son propre record précédent.
# Contrainte chaud : valeurs strictement croissantes dans le temps par station.
# Contrainte froid : valeurs strictement décroissantes dans le temps par station.

_FAKE_HOT_RECORDS: list[TemperatureRecordEntry] = [
    # ORLY : 3 records progressifs de chaud
    TemperatureRecordEntry("07149", "ORLY", "94", 32.1, dt.date(1947, 7, 19)),
    TemperatureRecordEntry("07149", "ORLY", "94", 38.0, dt.date(2003, 8, 9)),
    TemperatureRecordEntry("07149", "ORLY", "94", 42.6, dt.date(2019, 7, 25)),
    # BOURGES : 2 records progressifs de chaud
    TemperatureRecordEntry("07255", "BOURGES", "18", 33.5, dt.date(1947, 7, 19)),
    TemperatureRecordEntry("07255", "BOURGES", "18", 41.8, dt.date(2019, 7, 25)),
    # TOULOUSE-BLAGNAC : 2 records progressifs de chaud
    TemperatureRecordEntry(
        "07630", "TOULOUSE-BLAGNAC", "31", 35.0, dt.date(2003, 6, 28)
    ),
    TemperatureRecordEntry(
        "07630", "TOULOUSE-BLAGNAC", "31", 44.0, dt.date(2019, 6, 28)
    ),
    # LYON-BRON : 2 records progressifs de chaud
    TemperatureRecordEntry("07481", "LYON-BRON", "69", 37.2, dt.date(1947, 8, 5)),
    TemperatureRecordEntry("07481", "LYON-BRON", "69", 40.5, dt.date(2003, 8, 12)),
]

_FAKE_COLD_RECORDS: list[TemperatureRecordEntry] = [
    # ORLY : 3 records progressifs de froid
    TemperatureRecordEntry("07149", "ORLY", "94", -5.0, dt.date(1963, 1, 15)),
    TemperatureRecordEntry("07149", "ORLY", "94", -12.5, dt.date(1972, 2, 3)),
    TemperatureRecordEntry("07149", "ORLY", "94", -18.2, dt.date(1985, 1, 17)),
    # BOURGES : 2 records progressifs de froid
    TemperatureRecordEntry("07255", "BOURGES", "18", -10.0, dt.date(1956, 2, 12)),
    TemperatureRecordEntry("07255", "BOURGES", "18", -20.5, dt.date(1985, 1, 16)),
    # TOULOUSE-BLAGNAC : 2 records progressifs de froid
    TemperatureRecordEntry(
        "07630", "TOULOUSE-BLAGNAC", "31", -8.0, dt.date(1963, 2, 3)
    ),
    TemperatureRecordEntry(
        "07630", "TOULOUSE-BLAGNAC", "31", -15.0, dt.date(1985, 1, 16)
    ),
]


class FakeTemperatureRecordsDataSource:
    """
    Data source fake pour les records progressifs de température.
    Retourne des données déterministes avec plusieurs lignes par station.
    Pas de dépendances externes, pur Python.
    """

    def fetch_records(
        self, request: TemperatureRecordsRequest
    ) -> TemperatureRecordsResult:
        results = list(
            _FAKE_HOT_RECORDS if request.type_records == "hot" else _FAKE_COLD_RECORDS
        )

        if request.date_start:
            results = [e for e in results if e.record_date >= request.date_start]
        if request.date_end:
            results = [e for e in results if e.record_date <= request.date_end]

        if request.territoire == "department":
            results = [e for e in results if e.department == request.territoire_id]
        elif request.territoire == "station":
            results = [e for e in results if e.station_id == request.territoire_id]
        elif request.territoire == "region":
            from weather.regions import departments_for_region

            depts = set(departments_for_region(request.territoire_id or ""))
            results = [e for e in results if e.department in depts]

        total_count = len(results)

        page = request.page
        page_size = request.page_size

        start = (page - 1) * page_size
        end = start + page_size

        paginated = results[start:end]

        total_pages = (total_count + page_size - 1) // page_size

        return TemperatureRecordsResult(
            entries=paginated,
            pagination=Pagination(
                total_count=total_count,
                page=page,
                page_size=page_size,
                total_pages=total_pages,
            ),
        )
