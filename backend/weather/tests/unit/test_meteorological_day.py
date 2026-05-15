"""
Tests unitaires des helpers `meteorological_tn_day` / `meteorological_tx_day`
de `weather.tests.helpers.meteorological_day`.

Ces helpers reproduisent la convention SQL de `v_quotidienne_realtime` :
- `tn(D)` = MIN sur la fenêtre (D-1 18:00:01 → D 18:00:00)
- `tx(D)` = MAX sur la fenêtre (D 06:00:01 → D+1 06:00:00)

Les datetimes utilisés ci-dessous sont explicitement UTC (`Z`).
"""

from __future__ import annotations

import datetime as dt

import pytest

from weather.tests.helpers.meteorological_day import (
    meteorological_tn_day,
    meteorological_tx_day,
)


@pytest.mark.parametrize(
    ("reading", "expected_day"),
    [
        # Avant la frontière 18 h → reste dans la journée calendaire
        ("2026-05-15T00:00:00Z", "2026-05-15"),
        ("2026-05-15T03:00:00Z", "2026-05-15"),
        ("2026-05-15T12:00:00Z", "2026-05-15"),
        # Frontière inclusive : 18:00:00 reste dans la journée
        ("2026-05-15T18:00:00Z", "2026-05-15"),
        # Après la frontière → bascule sur le lendemain
        ("2026-05-15T18:00:01Z", "2026-05-16"),
        ("2026-05-15T23:59:59Z", "2026-05-16"),
    ],
)
def test_meteorological_tn_day(reading: str, expected_day: str) -> None:
    assert meteorological_tn_day(dt.datetime.fromisoformat(reading)) == (
        dt.date.fromisoformat(expected_day)
    )


@pytest.mark.parametrize(
    ("reading", "expected_day"),
    [
        # Avant la frontière 6 h → reste dans la journée précédente
        ("2026-05-15T00:00:00Z", "2026-05-14"),
        ("2026-05-15T05:59:59Z", "2026-05-14"),
        # Frontière inclusive : 06:00:00 reste dans la journée précédente
        ("2026-05-15T06:00:00Z", "2026-05-14"),
        # Après la frontière → bascule sur la journée calendaire
        ("2026-05-15T06:00:01Z", "2026-05-15"),
        ("2026-05-15T12:00:00Z", "2026-05-15"),
        ("2026-05-15T22:00:00Z", "2026-05-15"),
    ],
)
def test_meteorological_tx_day(reading: str, expected_day: str) -> None:
    assert meteorological_tx_day(dt.datetime.fromisoformat(reading)) == (
        dt.date.fromisoformat(expected_day)
    )
