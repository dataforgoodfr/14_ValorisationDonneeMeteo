"""
Tests d'intégration pour TimescaleNationalIndicatorAbsoluteExtremesDataSource.

Ces tests vérifient que la data source lit correctement les valeurs
depuis les vues v_itn_absolute_extremes_daily/monthly/yearly.

Patterns :
- pytestmark = pytest.mark.django_db pour l'accès base de données
"""

from __future__ import annotations

import pytest

from weather.data_sources.timescale import (
    TimescaleNationalIndicatorAbsoluteExtremesDataSource,
)
from weather.tests.helpers.itn import insert_itn_daily

pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------------------
# fetch_daily_absolute_extremes
# ---------------------------------------------------------------------------


def test_daily_absolute_extremes_returns_matching_pairs():
    insert_itn_daily(2000, 1, 1, 2.0)
    insert_itn_daily(2025, 1, 1, 7.0)
    insert_itn_daily(2000, 3, 1, 5.0)
    insert_itn_daily(2025, 3, 1, 8.0)
    insert_itn_daily(2000, 6, 15, 20.0)
    insert_itn_daily(2025, 6, 15, 25.0)

    ds = TimescaleNationalIndicatorAbsoluteExtremesDataSource()
    result = ds.fetch_daily_absolute_extremes({(1, 1), (3, 1)})

    assert set(result.keys()) == {(1, 1), (3, 1)}
    assert result[(1, 1)].absolute_min == pytest.approx(2.0)
    assert result[(1, 1)].absolute_max == pytest.approx(7.0)
    assert result[(3, 1)].absolute_min == pytest.approx(5.0)
    assert result[(3, 1)].absolute_max == pytest.approx(8.0)
    # (6, 15) not requested → not in result
    assert (6, 15) not in result


def test_daily_absolute_extremes_filters_unrequested_pairs():
    insert_itn_daily(2000, 5, 1, 10.0)
    insert_itn_daily(2000, 5, 2, 999.0)

    ds = TimescaleNationalIndicatorAbsoluteExtremesDataSource()
    result = ds.fetch_daily_absolute_extremes({(5, 1)})

    assert list(result.keys()) == [(5, 1)]
    assert result[(5, 1)].absolute_min == pytest.approx(10.0)
    assert result[(5, 1)].absolute_max == pytest.approx(10.0)


def test_daily_absolute_extremes_empty_input_returns_empty():
    ds = TimescaleNationalIndicatorAbsoluteExtremesDataSource()
    assert ds.fetch_daily_absolute_extremes(set()) == {}


def test_daily_absolute_extremes_requested_pair_absent_returns_empty():
    """Un (month, day_of_month) absent de la MV n'est pas retourné."""
    insert_itn_daily(2000, 1, 1, 5.0)
    insert_itn_daily(2025, 1, 1, 10.0)

    ds = TimescaleNationalIndicatorAbsoluteExtremesDataSource()
    result = ds.fetch_daily_absolute_extremes({(12, 31)})

    assert result == {}


# ---------------------------------------------------------------------------
# fetch_monthly_absolute_extremes
# ---------------------------------------------------------------------------


def test_monthly_absolute_extremes_returns_matching_months():
    insert_itn_daily(2000, 1, 1, 4.0)
    insert_itn_daily(2025, 1, 4, 7.0)
    insert_itn_daily(2000, 6, 1, 20.0)
    insert_itn_daily(2025, 6, 4, 22.0)

    ds = TimescaleNationalIndicatorAbsoluteExtremesDataSource()
    result = ds.fetch_monthly_absolute_extremes({1, 6})

    assert set(result.keys()) == {1, 6}
    assert result[1].absolute_min == pytest.approx(4.0)
    assert result[1].absolute_max == pytest.approx(7.0)
    assert result[6].absolute_min == pytest.approx(20.0)
    assert result[6].absolute_max == pytest.approx(22.0)


def test_monthly_absolute_extremes_filters_unrequested_months():
    insert_itn_daily(2000, 3, 1, 8.0)
    insert_itn_daily(2025, 3, 4, 12.0)
    insert_itn_daily(2000, 9, 1, 15.0)
    insert_itn_daily(2025, 9, 4, 18.0)

    ds = TimescaleNationalIndicatorAbsoluteExtremesDataSource()
    result = ds.fetch_monthly_absolute_extremes({3})

    assert list(result.keys()) == [3]
    assert result[3].absolute_min == pytest.approx(8.0)


def test_monthly_absolute_extremes_empty_input_returns_empty():
    ds = TimescaleNationalIndicatorAbsoluteExtremesDataSource()
    assert ds.fetch_monthly_absolute_extremes(set()) == {}


# ---------------------------------------------------------------------------
# fetch_yearly_absolute_extremes
# ---------------------------------------------------------------------------


def test_yearly_absolute_extremes_returns_values():
    insert_itn_daily(2000, 1, 2, 5.0)
    insert_itn_daily(2013, 3, 4, 6.5)
    insert_itn_daily(2025, 5, 6, 8.0)

    ds = TimescaleNationalIndicatorAbsoluteExtremesDataSource()
    result = ds.fetch_yearly_absolute_extremes()

    assert result.absolute_min == pytest.approx(5.0)
    assert result.absolute_max == pytest.approx(8.0)


def test_yearly_absolute_extremes_no_data_raises():
    """La table est vide → ValueError (même comportement que la baseline)."""
    ds = TimescaleNationalIndicatorAbsoluteExtremesDataSource()
    with pytest.raises(ValueError, match="extremes annuels"):
        ds.fetch_yearly_absolute_extremes()
