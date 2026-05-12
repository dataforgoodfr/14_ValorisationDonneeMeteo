"""
Tests d'intégration pour TimescaleNationalIndicatorAbsoluteExtremesDataSource.

Ces tests vérifient que la data source lit correctement les valeurs
depuis les tables mv_itn_absolute_extremes_daily/monthly/yearly.
En tests, ces tables sont des tables ordinaires (pas des MV) créées
par backend/sql/test_tables/itn_absolute_extremes.sql.

Patterns :
- insert_absolute_extremes_daily/monthly/yearly() depuis les helpers
- pytestmark = pytest.mark.django_db pour l'accès base de données
"""

from __future__ import annotations

import pytest

from weather.data_sources.timescale import (
    TimescaleNationalIndicatorAbsoluteExtremesDataSource,
)
from weather.tests.helpers.itn import (
    insert_absolute_extremes_daily,
    insert_absolute_extremes_monthly,
    insert_absolute_extremes_yearly,
)

pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------------------
# fetch_daily_absolute_extremes
# ---------------------------------------------------------------------------


def test_daily_absolute_extremes_returns_matching_pairs():
    insert_absolute_extremes_daily(1, 1, absolute_min=2.0, absolute_max=7.0)
    insert_absolute_extremes_daily(3, 1, absolute_min=5.0, absolute_max=8.0)
    insert_absolute_extremes_daily(6, 15, absolute_min=20.0, absolute_max=25.0)

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
    insert_absolute_extremes_daily(5, 1, absolute_min=10.0, absolute_max=10.0)
    insert_absolute_extremes_daily(5, 2, absolute_min=999.0, absolute_max=999.0)

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
    insert_absolute_extremes_daily(1, 1, absolute_min=5.0, absolute_max=10.0)

    ds = TimescaleNationalIndicatorAbsoluteExtremesDataSource()
    result = ds.fetch_daily_absolute_extremes({(12, 31)})

    assert result == {}


# ---------------------------------------------------------------------------
# fetch_monthly_absolute_extremes
# ---------------------------------------------------------------------------


def test_monthly_absolute_extremes_returns_matching_months():
    insert_absolute_extremes_monthly(1, absolute_min=4.0, absolute_max=7.0)
    insert_absolute_extremes_monthly(6, absolute_min=20.0, absolute_max=22.0)

    ds = TimescaleNationalIndicatorAbsoluteExtremesDataSource()
    result = ds.fetch_monthly_absolute_extremes({1, 6})

    assert set(result.keys()) == {1, 6}
    assert result[1].absolute_min == pytest.approx(4.0)
    assert result[1].absolute_max == pytest.approx(7.0)
    assert result[6].absolute_min == pytest.approx(20.0)
    assert result[6].absolute_max == pytest.approx(22.0)


def test_monthly_absolute_extremes_filters_unrequested_months():
    insert_absolute_extremes_monthly(3, absolute_min=8.0, absolute_max=12.0)
    insert_absolute_extremes_monthly(9, absolute_min=15.0, absolute_max=18.0)

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
    insert_absolute_extremes_yearly(absolute_min=5.0, absolute_max=8.0)

    ds = TimescaleNationalIndicatorAbsoluteExtremesDataSource()
    result = ds.fetch_yearly_absolute_extremes()

    assert result.absolute_min == pytest.approx(5.0)
    assert result.absolute_max == pytest.approx(8.0)


def test_yearly_absolute_extremes_no_data_raises():
    """La table est vide → ValueError (même comportement que la baseline)."""
    ds = TimescaleNationalIndicatorAbsoluteExtremesDataSource()
    with pytest.raises(ValueError, match="extremes annuels"):
        ds.fetch_yearly_absolute_extremes()
