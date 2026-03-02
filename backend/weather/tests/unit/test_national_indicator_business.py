from __future__ import annotations

import datetime as dt

from weather.data_sources.timescale import (
    compute_itn_for_day,
)
from weather.services.national_indicator.stations import (
    ITN_ALWAYS_STATION_CODES,
    REIMS_COURCY,
    REIMS_PRUNAY,
    REIMS_SWITCH_DATE,
    expected_reims_code,
    expected_station_codes,
)


def _build_station_code_to_fixed_temperature_map(
    day: dt.date,
    *,
    reims_station_temperature: float = 20.0,
    always_station_temperature: float = 10.0,
) -> dict[str, float]:
    """Construit un mapping complet (30 slots attendus pour ce jour)."""
    m = {code: always_station_temperature for code in ITN_ALWAYS_STATION_CODES}
    m[expected_reims_code(day)] = reims_station_temperature
    return m


def test_expected_station_codes_len_is_30():
    assert len(expected_station_codes(dt.date(2025, 1, 1))) == 30


def test_expected_station_codes_reims_before_switch_is_courcy():
    day = REIMS_SWITCH_DATE - dt.timedelta(days=1)  # 2012-05-07
    codes = expected_station_codes(day)
    assert REIMS_COURCY in codes
    assert REIMS_PRUNAY not in codes


def test_expected_station_codes_reims_at_switch_is_prunay():
    day = REIMS_SWITCH_DATE  # 2012-05-08
    codes = expected_station_codes(day)
    assert REIMS_PRUNAY in codes
    assert REIMS_COURCY not in codes


def test_compute_itn_ok_returns_mean_over_30_slots():
    day = dt.date(2025, 1, 1)
    m = _build_station_code_to_fixed_temperature_map(
        day, reims_station_temperature=40.0, always_station_temperature=10.0
    )
    itn = compute_itn_for_day(day, m)
    assert itn == (29 * 10.0 + 40.0) / 30.0


def test_compute_itn_drop_if_missing_any_always_station():
    day = dt.date(2025, 1, 1)
    m = _build_station_code_to_fixed_temperature_map(day)
    m.pop(next(iter(ITN_ALWAYS_STATION_CODES)))
    assert compute_itn_for_day(day, m) is None


def test_compute_itn_drop_if_missing_expected_reims():
    day = dt.date(2025, 1, 1)
    m = {code: 10.0 for code in ITN_ALWAYS_STATION_CODES}
    # pas de Reims attendue => drop
    assert compute_itn_for_day(day, m) is None


def test_compute_itn_accepts_double_reims_and_keeps_expected_one():
    # après le pivot => Prunay attendue
    day = REIMS_SWITCH_DATE
    m = _build_station_code_to_fixed_temperature_map(
        day, reims_station_temperature=30.0, always_station_temperature=10.0
    )
    # ajoute l'autre Reims (Courcy) avec une valeur "piège"
    m[REIMS_COURCY] = 999.0

    itn = compute_itn_for_day(day, m)
    # doit prendre Prunay (30.0), pas 999.0
    assert itn == (29 * 10.0 + 30.0) / 30.0


def test_compute_itn_drop_if_extra_station_not_allowed():
    day = dt.date(2025, 1, 1)
    m = _build_station_code_to_fixed_temperature_map(day)
    m["99999999"] = 12.3  # station parasite
    assert compute_itn_for_day(day, m) is None
