"""
Tests de régression : 29 février synthétique dans les extremes absolus.

Contexte du bug :
    Les extrêmes mensuels/annuels incluaient les jours fictifs (is_fictive=True)
    dans le calcul de la moyenne. En année non-bissextile, le 29 fév synthétique
    (interpolé entre fév 28 et mars 1) abaissait la moyenne → absolute_max < itn observé.

Fix : les MVs 009 et 010 filtrent WHERE NOT is_fictive pour les agrégations
      mensuelles et annuelles. La MV 008 (journalière) conserve les fictifs
      pour avoir une valeur au jour calendaire (2, 29).
"""

from __future__ import annotations

import pytest

from weather.data_sources.timescale import (
    TimescaleNationalIndicatorAbsoluteExtremesDataSource,
)
from weather.tests.helpers.itn import (
    insert_itn_daily_with_feb29,
    refresh_absolute_extremes_mvs,
)

pytestmark = pytest.mark.django_db

ds = TimescaleNationalIndicatorAbsoluteExtremesDataSource()


def test_monthly_absolute_max_excludes_synthetic_feb29():
    """
    Année 2023 (non-bissextile) :
      - fév 28 réel   itn = 10.0
      - fév 29 fictif itn =  5.0   ← interpolé, ne doit pas compter

    Avec le bug : moyenne fév = (10.0 + 5.0) / 2 = 7.5  → absolute_max = 7.5
    Fix attendu : moyenne fév = 10.0                     → absolute_max = 10.0
    """
    insert_itn_daily_with_feb29(2023, 2, 28, itn=10.0)
    insert_itn_daily_with_feb29(2023, 2, 29, itn=5.0, is_fictive=True)
    refresh_absolute_extremes_mvs()

    result = ds.fetch_monthly_absolute_extremes({2})

    assert result[2].absolute_max == pytest.approx(10.0)  # pas 7.5
    assert result[2].absolute_min == pytest.approx(10.0)


def test_yearly_absolute_max_excludes_synthetic_feb29():
    """
    Année 2025 (non-bissextile) :
      - jan 1  réel   itn = 14.0
      - fév 29 fictif itn =  0.0   ← interpolé, ne doit pas compter

    Avec le bug : moyenne 2025 = (14.0 + 0.0) / 2 = 7.0  → absolute_max = 7.0
    Fix attendu : moyenne 2025 = 14.0                    → absolute_max = 14.0
    """
    insert_itn_daily_with_feb29(2025, 1, 1, itn=14.0)
    insert_itn_daily_with_feb29(2025, 2, 29, itn=0.0, is_fictive=True)
    refresh_absolute_extremes_mvs()

    result = ds.fetch_yearly_absolute_extremes()

    assert result.absolute_max == pytest.approx(14.0)  # pas 7.0


def test_daily_absolute_extremes_include_synthetic_feb29():
    """
    Le jour calendaire (2, 29) doit avoir des extrêmes même en année non-bissextile.
    Les lignes fictives sont intentionnellement incluses dans le calcul journalier.
    """
    insert_itn_daily_with_feb29(2023, 2, 28, itn=10.0)
    insert_itn_daily_with_feb29(2023, 2, 29, itn=5.0, is_fictive=True)
    refresh_absolute_extremes_mvs()

    result = ds.fetch_daily_absolute_extremes({(2, 29)})

    assert (2, 29) in result
    assert result[(2, 29)].absolute_min == pytest.approx(5.0)
    assert result[(2, 29)].absolute_max == pytest.approx(5.0)


def test_absolute_extremes_ignore_data_before_1946():
    """
    Les données antérieures à 1946 ne doivent pas être prises en compte.
    Le filtrage est effectué en amont dans mv_itn_daily_all_years (006) via
    AND q.date >= DATE '1946-01-01', reproduit ici dans insert_itn_daily_with_feb29.
    Scénario :
      - 1900 jan 1 : itn =  0.0  ← filtré en amont, ne doit pas compter
      - 2000 jan 1 : itn = 14.0  ← après le seuil, compte
    absolute_min et absolute_max doivent être déterminés par 2000 uniquement (14.0).
    """
    insert_itn_daily_with_feb29(1900, 1, 1, itn=0.0)
    insert_itn_daily_with_feb29(2000, 1, 1, itn=14.0)
    refresh_absolute_extremes_mvs()

    daily = ds.fetch_daily_absolute_extremes({(1, 1)})
    assert daily[(1, 1)].absolute_min == pytest.approx(14.0)
    assert daily[(1, 1)].absolute_max == pytest.approx(14.0)

    monthly = ds.fetch_monthly_absolute_extremes({1})
    assert monthly[1].absolute_min == pytest.approx(14.0)
    assert monthly[1].absolute_max == pytest.approx(14.0)

    yearly = ds.fetch_yearly_absolute_extremes()
    assert yearly.absolute_min == pytest.approx(14.0)
    assert yearly.absolute_max == pytest.approx(14.0)
