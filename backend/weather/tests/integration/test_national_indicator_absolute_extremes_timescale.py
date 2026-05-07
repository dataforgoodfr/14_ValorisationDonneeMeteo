"""
Tests d'intégration pour TimescaleNationalIndicatorAbsoluteExtremesDataSource.

Ces tests vérifient le calcul SQL des extremes absolus historiques de l'ITN
en insérant des données dans la base de test et en comparant les résultats.

Patterns :
- insert_quotidienne() depuis les helpers existants
- pytestmark = pytest.mark.django_db pour l'accès base de données
- seed_itn_day() : fixture locale pour semer un jour ITN complet (30 stations)
"""

from __future__ import annotations

import datetime as dt
from collections.abc import Callable

import pytest

from weather.data_sources.timescale import (
    TimescaleNationalIndicatorAbsoluteExtremesDataSource,
)
from weather.services.national_indicator.stations import (
    ITN_ALWAYS_STATION_CODES,
    expected_reims_code,
)
from weather.tests.helpers.itn import insert_quotidienne

pytestmark = pytest.mark.django_db


@pytest.fixture()
def seed_itn_day() -> Callable[..., None]:
    """
    Insère un jour ITN complet pour les 30 stations de référence.
    always_val : valeur tntxm pour les 29 stations fixes.
    reims_val  : valeur tntxm pour la station Reims active ce jour-là.
    """

    def _seed(
        day: dt.date,
        *,
        always_val: float = 10.0,
        reims_val: float | None = None,
    ) -> None:
        if reims_val is None:
            reims_val = always_val
        for code in ITN_ALWAYS_STATION_CODES:
            insert_quotidienne(day, code, always_val)
        insert_quotidienne(day, expected_reims_code(day), reims_val)

    return _seed


# ---------------------------------------------------------------------------
# fetch_daily_absolute_extremes
# ---------------------------------------------------------------------------


def test_daily_absolute_extremes_min_max_across_years(
    seed_itn_day: Callable[..., None],
):
    """
    Insère Jan 1 sur 3 années avec des ITN différents.
    Expected : absolute_min = min des 3 ITN, absolute_max = max des 3.
    """
    # Toutes les stations valent always_val => ITN = always_val
    seed_itn_day(dt.date(2022, 1, 1), always_val=4.0)  # ITN = 4.0
    seed_itn_day(dt.date(2023, 1, 1), always_val=7.0)  # ITN = 7.0
    seed_itn_day(dt.date(2024, 1, 1), always_val=2.0)  # ITN = 2.0

    ds = TimescaleNationalIndicatorAbsoluteExtremesDataSource()
    result = ds.fetch_daily_absolute_extremes({(1, 1)})

    assert (1, 1) in result
    assert result[(1, 1)].absolute_min == pytest.approx(2.0)
    assert result[(1, 1)].absolute_max == pytest.approx(7.0)


def test_daily_absolute_extremes_multiple_calendar_days(
    seed_itn_day: Callable[..., None],
):
    """Deux jours calendaires différents retournent des extremes indépendants."""
    seed_itn_day(dt.date(2022, 3, 1), always_val=5.0)
    seed_itn_day(dt.date(2023, 3, 1), always_val=8.0)
    seed_itn_day(dt.date(2022, 6, 15), always_val=20.0)
    seed_itn_day(dt.date(2023, 6, 15), always_val=25.0)

    ds = TimescaleNationalIndicatorAbsoluteExtremesDataSource()
    result = ds.fetch_daily_absolute_extremes({(3, 1), (6, 15)})

    assert result[(3, 1)].absolute_min == pytest.approx(5.0)
    assert result[(3, 1)].absolute_max == pytest.approx(8.0)
    assert result[(6, 15)].absolute_min == pytest.approx(20.0)
    assert result[(6, 15)].absolute_max == pytest.approx(25.0)


def test_daily_absolute_extremes_incomplete_day_excluded(
    seed_itn_day: Callable[..., None],
):
    """
    Un jour avec moins de 29 stations ne doit pas être inclus dans le calcul.
    29 stations est désormais accepté (HAVING COUNT >= 29) ; il faut donc
    insérer seulement 28 stations pour vérifier l'exclusion.
    """
    # Jour valide (30 stations)
    seed_itn_day(dt.date(2022, 5, 1), always_val=10.0)
    # Jour incomplet : on insère seulement 28 stations fixes (pas Reims, pas une des fixes)
    # => 28 stations => HAVING COUNT(DISTINCT station_code) = 28 < 29 => exclu
    day_incomplete = dt.date(2023, 5, 1)
    for code in list(ITN_ALWAYS_STATION_CODES)[:-1]:  # 28 stations
        insert_quotidienne(day_incomplete, code, 999.0)

    ds = TimescaleNationalIndicatorAbsoluteExtremesDataSource()
    result = ds.fetch_daily_absolute_extremes({(5, 1)})

    # Seul le jour valide (2022) contribue : min = max = 10.0
    assert result[(5, 1)].absolute_min == pytest.approx(10.0)
    assert result[(5, 1)].absolute_max == pytest.approx(10.0)


def test_daily_absolute_extremes_empty_input_returns_empty():
    ds = TimescaleNationalIndicatorAbsoluteExtremesDataSource()
    assert ds.fetch_daily_absolute_extremes(set()) == {}


# ---------------------------------------------------------------------------
# fetch_monthly_absolute_extremes
# ---------------------------------------------------------------------------


def test_monthly_absolute_extremes_min_max_across_years(
    seed_itn_day: Callable[..., None],
):
    """
    Janvier 2022 : ITN journalier = 4.0 => moyenne mensuelle = 4.0
    Janvier 2023 : ITN journalier = 7.0 => moyenne mensuelle = 7.0
    => absolute_min=4.0, absolute_max=7.0
    """
    # Semer les 31 jours de Janvier pour deux années
    for d in range(1, 32):
        seed_itn_day(dt.date(2022, 1, d), always_val=4.0)
        seed_itn_day(dt.date(2023, 1, d), always_val=7.0)

    ds = TimescaleNationalIndicatorAbsoluteExtremesDataSource()
    result = ds.fetch_monthly_absolute_extremes({1})

    assert 1 in result
    assert result[1].absolute_min == pytest.approx(4.0)
    assert result[1].absolute_max == pytest.approx(7.0)


def test_monthly_absolute_extremes_two_months_independent(
    seed_itn_day: Callable[..., None],
):
    # Janvier 2022 : ITN = 3.0 / Janvier 2023 : ITN = 5.0
    for d in range(1, 32):
        seed_itn_day(dt.date(2022, 1, d), always_val=3.0)
        seed_itn_day(dt.date(2023, 1, d), always_val=5.0)
    # Juin 2022 : ITN = 20.0 / Juin 2023 : ITN = 22.0
    for d in range(1, 31):
        seed_itn_day(dt.date(2022, 6, d), always_val=20.0)
        seed_itn_day(dt.date(2023, 6, d), always_val=22.0)

    ds = TimescaleNationalIndicatorAbsoluteExtremesDataSource()
    result = ds.fetch_monthly_absolute_extremes({1, 6})

    assert result[1].absolute_min == pytest.approx(3.0)
    assert result[1].absolute_max == pytest.approx(5.0)
    assert result[6].absolute_min == pytest.approx(20.0)
    assert result[6].absolute_max == pytest.approx(22.0)


def test_monthly_absolute_extremes_empty_input_returns_empty():
    ds = TimescaleNationalIndicatorAbsoluteExtremesDataSource()
    assert ds.fetch_monthly_absolute_extremes(set()) == {}


# ---------------------------------------------------------------------------
# fetch_yearly_absolute_extremes
# ---------------------------------------------------------------------------


def test_yearly_absolute_extremes_min_max_across_years(
    seed_itn_day: Callable[..., None],
):
    """
    2022 entier : ITN = 5.0 => moyenne annuelle = 5.0
    2023 entier : ITN = 8.0 => moyenne annuelle = 8.0
    => absolute_min=5.0, absolute_max=8.0
    """
    # Semer juste un mois pour approximer la moyenne annuelle (seuls jours disponibles)
    for d in range(1, 32):
        seed_itn_day(dt.date(2022, 1, d), always_val=5.0)
    for d in range(1, 32):
        seed_itn_day(dt.date(2023, 1, d), always_val=8.0)

    ds = TimescaleNationalIndicatorAbsoluteExtremesDataSource()
    result = ds.fetch_yearly_absolute_extremes()

    assert result.absolute_min == pytest.approx(5.0)
    assert result.absolute_max == pytest.approx(8.0)
