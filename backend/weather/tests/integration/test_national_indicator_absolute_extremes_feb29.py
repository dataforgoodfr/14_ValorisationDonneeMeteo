"""
Tests de régression : 29 février synthétique dans les extremes absolus.

Vérifie que les agrégations mensuelles et annuelles excluent les jours fictifs
(29 fév synthétique pour les années non-bissextiles), de façon à rester cohérentes
avec le calcul de la température observée dans le service.

Contexte du bug :
    mv_itn_absolute_extremes_monthly/yearly était calculé depuis
    mv_itn_daily_all_years_with_feb29 sans filtrer les jours fictifs.
    Pour les années non-bissextiles, l'ajout d'un 29 fév synthétique =
    (itn_28fév + itn_1mar) / 2 modifiait la moyenne mensuelle/annuelle,
    la rendant différente de ce que le service calcule (jours réels uniquement).
    Résultat : absolute_max < température observée.

Invariant attendu (toujours vérifié par ces tests) :
    absolute_max >= max(températures observées pour la même période)
"""

from __future__ import annotations

import datetime as dt

import pytest

from weather.data_sources.timescale import (
    TimescaleNationalIndicatorAbsoluteExtremesDataSource,
)
from weather.tests.helpers.itn import (
    insert_itn_day_values,
    seed_absolute_extremes_from_quotidienne,
)

pytestmark = pytest.mark.django_db


def test_monthly_absolute_max_excludes_synthetic_feb29():
    """
    Régression : absolute_max mensuel ne doit pas être dilué par le 29 fév synthétique.

    Données :
    - 2023 (non-bissextile) :
        - 28 fév : ITN = 10.0  (seul jour réel de février)
        - 1 mar  : ITN =  0.0  → 29 fév synthétique = (10.0 + 0.0) / 2 = 5.0
      Moyenne fév réelle    = 10.0
      Moyenne fév avec fictif = (10.0 + 5.0) / 2 = 7.5  ← < 10.0 (bug)
      Moyenne fév sans fictif = 10.0                      ← correct

    absolute_max pour février doit être 10.0, pas 7.5.
    """
    insert_itn_day_values(dt.date(2023, 2, 28), 10.0)
    insert_itn_day_values(dt.date(2023, 3, 1), 0.0)

    seed_absolute_extremes_from_quotidienne()

    ds = TimescaleNationalIndicatorAbsoluteExtremesDataSource()
    result = ds.fetch_monthly_absolute_extremes({2})

    assert result[2].absolute_max == pytest.approx(10.0)
    assert result[2].absolute_min == pytest.approx(10.0)


def test_monthly_absolute_max_not_below_observed_temperature():
    """
    Invariant général : absolute_max >= température observée pour chaque mois.

    Deux années, février :
    - 2023 (non-bissextile) : 28 fév = 10.0, 1 mar = 0.0
    - 2024 (bissextile)     : 28 fév = 5.0, 29 fév = 5.0 (réel), 1 mar = 5.0

    Températures observées :
    - fév 2023 (réel) = 10.0
    - fév 2024 (réel) = 5.0

    absolute_max pour fév doit être >= max(10.0, 5.0) = 10.0.
    """
    insert_itn_day_values(dt.date(2023, 2, 28), 10.0)
    insert_itn_day_values(dt.date(2023, 3, 1), 0.0)
    insert_itn_day_values(dt.date(2024, 2, 28), 5.0)
    insert_itn_day_values(dt.date(2024, 2, 29), 5.0)
    insert_itn_day_values(dt.date(2024, 3, 1), 5.0)

    seed_absolute_extremes_from_quotidienne()

    ds = TimescaleNationalIndicatorAbsoluteExtremesDataSource()
    result = ds.fetch_monthly_absolute_extremes({2})

    # 10.0 est la température observée max pour février → absolute_max doit être >= 10.0
    assert result[2].absolute_max >= 10.0 - 1e-9


def test_daily_absolute_extremes_include_synthetic_feb29():
    """
    Vérifie que le 29 fév synthétique EST inclus pour les extremes journaliers.
    C'est le comportement attendu : on veut une valeur pour le jour calendaire (2, 29)
    même pour les années non-bissextiles.
    """
    insert_itn_day_values(dt.date(2023, 2, 28), 10.0)
    insert_itn_day_values(dt.date(2023, 3, 1), 0.0)

    seed_absolute_extremes_from_quotidienne()

    ds = TimescaleNationalIndicatorAbsoluteExtremesDataSource()
    result = ds.fetch_daily_absolute_extremes({(2, 29)})

    # Synthétique = (10.0 + 0.0) / 2 = 5.0
    assert (2, 29) in result
    assert result[(2, 29)].absolute_min == pytest.approx(5.0)
    assert result[(2, 29)].absolute_max == pytest.approx(5.0)
