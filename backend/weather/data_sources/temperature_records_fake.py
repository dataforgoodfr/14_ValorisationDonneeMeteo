from __future__ import annotations

import datetime as dt

from weather.services.temperature_records.types import (
    TemperatureRecordEntry,
    TemperatureRecordsRequest,
)

# Données fake déterministes pour les records progressifs de température.
# Plusieurs lignes par station : chaque ligne est une fois où la station a
# battu son propre record précédent.
# Contrainte chaud : valeurs strictement croissantes dans le temps par station.
# Contrainte froid : valeurs strictement décroissantes dans le temps par station.

_FAKE_HOT_RECORDS: list[TemperatureRecordEntry] = [
    # ORLY : 3 records progressifs de chaud
    TemperatureRecordEntry(
        "07149",
        "ORLY",
        "94",
        32.1,
        dt.date(1947, 7, 19),
        lat=48.718,
        lon=2.397,
        alt=86.0,
    ),
    TemperatureRecordEntry(
        "07149",
        "ORLY",
        "94",
        38.0,
        dt.date(2003, 8, 9),
        lat=48.718,
        lon=2.397,
        alt=86.0,
    ),
    TemperatureRecordEntry(
        "07149",
        "ORLY",
        "94",
        42.6,
        dt.date(2019, 7, 25),
        lat=48.718,
        lon=2.397,
        alt=86.0,
    ),
    # BOURGES : 2 records progressifs de chaud
    TemperatureRecordEntry(
        "07255",
        "BOURGES",
        "18",
        33.5,
        dt.date(1947, 7, 19),
        lat=47.059167,
        lon=2.359833,
        alt=161.0,
    ),
    TemperatureRecordEntry(
        "07255",
        "BOURGES",
        "18",
        41.8,
        dt.date(2019, 7, 25),
        lat=47.059167,
        lon=2.359833,
        alt=161.0,
    ),
    # TOULOUSE-BLAGNAC : 2 records progressifs de chaud
    TemperatureRecordEntry(
        "07630",
        "TOULOUSE-BLAGNAC",
        "31",
        35.0,
        dt.date(2003, 6, 28),
        lat=43.621,
        lon=1.378833,
        alt=151.0,
    ),
    TemperatureRecordEntry(
        "07630",
        "TOULOUSE-BLAGNAC",
        "31",
        44.0,
        dt.date(2019, 6, 28),
        lat=43.621,
        lon=1.378833,
        alt=151.0,
    ),
    # LYON-BRON : 2 records progressifs de chaud
    TemperatureRecordEntry(
        "07481",
        "LYON-BRON",
        "69",
        37.2,
        dt.date(1947, 8, 5),
        lat=45.721333,
        lon=4.949167,
        alt=202.0,
    ),
    TemperatureRecordEntry(
        "07481",
        "LYON-BRON",
        "69",
        40.5,
        dt.date(2003, 8, 12),
        lat=45.721333,
        lon=4.949167,
        alt=202.0,
    ),
]

_FAKE_COLD_RECORDS: list[TemperatureRecordEntry] = [
    # ORLY : 3 records progressifs de froid
    TemperatureRecordEntry(
        "07149",
        "ORLY",
        "94",
        -5.0,
        dt.date(1963, 1, 15),
        lat=48.718,
        lon=2.397,
        alt=86.0,
    ),
    TemperatureRecordEntry(
        "07149",
        "ORLY",
        "94",
        -12.5,
        dt.date(1972, 2, 3),
        lat=48.718,
        lon=2.397,
        alt=86.0,
    ),
    TemperatureRecordEntry(
        "07149",
        "ORLY",
        "94",
        -18.2,
        dt.date(1985, 1, 17),
        lat=48.718,
        lon=2.397,
        alt=86.0,
    ),
    # BOURGES : 2 records progressifs de froid
    TemperatureRecordEntry(
        "07255",
        "BOURGES",
        "18",
        -10.0,
        dt.date(1956, 2, 12),
        lat=47.059167,
        lon=2.359833,
        alt=161.0,
    ),
    TemperatureRecordEntry(
        "07255",
        "BOURGES",
        "18",
        -20.5,
        dt.date(1985, 1, 16),
        lat=47.059167,
        lon=2.359833,
        alt=161.0,
    ),
    # TOULOUSE-BLAGNAC : 2 records progressifs de froid
    TemperatureRecordEntry(
        "07630",
        "TOULOUSE-BLAGNAC",
        "31",
        -8.0,
        dt.date(1963, 2, 3),
        lat=43.621,
        lon=1.378833,
        alt=151.0,
    ),
    TemperatureRecordEntry(
        "07630",
        "TOULOUSE-BLAGNAC",
        "31",
        -15.0,
        dt.date(1985, 1, 16),
        lat=43.621,
        lon=1.378833,
        alt=151.0,
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
    ) -> list[TemperatureRecordEntry]:
        if request.type_records == "hot":
            return list(_FAKE_HOT_RECORDS)
        return list(_FAKE_COLD_RECORDS)
