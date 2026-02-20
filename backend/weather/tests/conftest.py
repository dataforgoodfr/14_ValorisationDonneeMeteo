from __future__ import annotations

import datetime as dt

import pytest

from weather.factories.weather import QuotidienneFactory
from weather.models import Station
from weather.services.national_indicator.stations import (
    ITN_ALWAYS_STATION_CODES,
    REIMS_COURCY,
    REIMS_PRUNAY,
    expected_reims_code,
)


def make_station(code: str) -> Station:
    return Station.objects.create(
        code=code,
        nom=f"ITN {code}",
        lat=1.0,
        lon=1.0,
        alt=1.0,
        departement=0,
        type_poste=0,  # IntegerField
        poste_public=True,
        poste_ouvert=True,
        frequence="horaire",
    )


@pytest.fixture()
def itn_stations(db) -> dict[str, Station]:
    codes = set(ITN_ALWAYS_STATION_CODES) | {REIMS_COURCY, REIMS_PRUNAY}
    return {code: make_station(code) for code in codes}


@pytest.fixture()
def seed_itn_day(itn_stations):
    """
    Helper: seed un jour complet ITN (29 always + Reims attendue) dans Quotidienne.
    """

    def _seed(
        day: dt.date, *, always_val: float = 10.0, reims_val: float = 20.0
    ) -> None:
        for code in ITN_ALWAYS_STATION_CODES:
            QuotidienneFactory(station=itn_stations[code], date=day, tntxm=always_val)

        reims_code = expected_reims_code(day)
        QuotidienneFactory(station=itn_stations[reims_code], date=day, tntxm=reims_val)

    return _seed
