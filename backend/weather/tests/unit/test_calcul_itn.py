import numpy as np
import pandas as pd
import pytest

from weather.calcul_itn import (
    DEFAULT_ITN_STATIONS_LIST,
    REIMS_COURCY_ID,
    REIMS_PRUNAY_ID,
    calculate_return_itn,
    correct_temperatures_Reims,
    itn_calculation,
    separate_by_station,
)

NAN = float("nan")


# ── Helpers ──────────────────────────────────────────────────────────


def _make_pivoted(dates, columns_data):
    """
    Build a pivoted DataFrame matching the shape of separate_by_station output.
    columns_data: dict mapping (metric, station_name) → list of values.
    """
    df = pd.DataFrame(columns_data, index=dates)
    df.index.name = "date"
    df.columns = pd.MultiIndex.from_tuples(df.columns, names=[None, "nom"])
    return df


def _make_gateway(stations_df, temp_daily):
    """Wrap fixed DataFrames into a gateway callable."""

    def gateway(stations_itn=None):
        return stations_df, temp_daily

    return gateway


# ── separate_by_station ─────────────────────────────────────────────


class TestSeparateByStation:
    def test_single_station_single_value(self):
        dates = pd.date_range("2024-01-01", periods=2, freq="D")
        df = pd.DataFrame(
            {
                "date": [dates[0], dates[1]],
                "nom": ["S", "S"],
                "tntxm": [7.0, 8.0],
            }
        )

        result = separate_by_station(
            df, index="date", columns="nom", values=["tntxm"], freq="D"
        )

        expected = _make_pivoted(dates, {("tntxm", "S"): [7.0, 8.0]})
        pd.testing.assert_frame_equal(result, expected)

    def test_multiple_stations(self):
        dates = pd.date_range("2024-01-01", periods=2, freq="D")
        df = pd.DataFrame(
            {
                "date": [dates[0], dates[1], dates[0], dates[1]],
                "nom": ["A", "A", "B", "B"],
                "tntxm": [5.0, 6.0, 10.0, 11.0],
            }
        )

        result = separate_by_station(
            df, index="date", columns="nom", values=["tntxm"], freq="D"
        )

        expected = _make_pivoted(
            dates,
            {
                ("tntxm", "A"): [5.0, 6.0],
                ("tntxm", "B"): [10.0, 11.0],
            },
        )
        pd.testing.assert_frame_equal(result, expected)

    def test_multiple_values(self):
        dates = pd.date_range("2024-01-01", periods=2, freq="D")
        df = pd.DataFrame(
            {
                "date": [dates[0], dates[1]],
                "nom": ["S", "S"],
                "temp_min": [4.0, 5.0],
                "tntxm": [7.0, 8.0],
            }
        )

        result = separate_by_station(
            df, index="date", columns="nom", values=["temp_min", "tntxm"], freq="D"
        )

        expected = _make_pivoted(
            dates,
            {
                ("temp_min", "S"): [4.0, 5.0],
                ("tntxm", "S"): [7.0, 8.0],
            },
        )
        pd.testing.assert_frame_equal(result, expected)

    def test_raises_on_missing_index(self):
        df = pd.DataFrame({"a": [1]})
        with pytest.raises(AssertionError, match="Cannot pivot"):
            separate_by_station(df, index="", columns="a", values=["a"])

    def test_raises_on_missing_columns(self):
        df = pd.DataFrame({"a": [1]})
        with pytest.raises(AssertionError, match="Cannot pivot"):
            separate_by_station(df, index="a", columns="", values=["a"])

    def test_raises_on_missing_values(self):
        df = pd.DataFrame({"a": [1]})
        with pytest.raises(AssertionError, match="Cannot pivot"):
            separate_by_station(df, index="a", columns="a", values="")


# ── correct_temperatures_Reims ──────────────────────────────────────


class TestCorrectTemperaturesReims:
    def test_applies_correction(self):
        dates = pd.date_range("2012-05-06", "2012-05-09", freq="D")
        input_df = _make_pivoted(
            dates,
            {
                ("tntxm", "Reims-Courcy"): [8.0, 9.0, 10.0, 11.0],
                ("tntxm", "Reims-Prunay"): [8.0, 9.0, 10.0, 11.0],
                ("tntxm", "Paris"): [11.0, 12.0, 13.0, 14.0],
            },
        )

        result = correct_temperatures_Reims(input_df)

        expected = _make_pivoted(
            dates,
            {
                ("tntxm", "Reims-Courcy"): [8.0, 9.0, NAN, NAN],
                ("tntxm", "Reims-Prunay"): [NAN, NAN, 10.0, 11.0],
                ("tntxm", "Paris"): [11.0, 12.0, 13.0, 14.0],
            },
        )
        pd.testing.assert_frame_equal(result, expected)

    def test_does_not_mutate_original(self):
        dates = pd.date_range("2012-05-06", "2012-05-09", freq="D")
        input_df = _make_pivoted(
            dates,
            {
                ("tntxm", "Reims-Courcy"): [8.0, 9.0, 10.0, 11.0],
                ("tntxm", "Reims-Prunay"): [8.0, 9.0, 10.0, 11.0],
            },
        )
        original = input_df.copy()

        correct_temperatures_Reims(input_df)

        pd.testing.assert_frame_equal(input_df, original)


# ── itn_calculation ─────────────────────────────────────────────────


class TestItnCalculation:
    def test_returns_mean_of_tntxm_across_stations(self):
        dates = pd.date_range("2024-01-01", periods=2, freq="D")
        df = _make_pivoted(
            dates,
            {
                ("tntxm", "A"): [10.0, 12.0],
                ("tntxm", "B"): [20.0, 22.0],
            },
        )

        result = itn_calculation(df)

        expected = pd.Series([15.0, 17.0], index=dates)
        pd.testing.assert_series_equal(result, expected, check_names=False)

    def test_ignores_nan_in_mean(self):
        dates = pd.date_range("2024-01-01", periods=2, freq="D")
        df = _make_pivoted(
            dates,
            {
                ("tntxm", "A"): [10.0, NAN],
                ("tntxm", "B"): [20.0, 22.0],
            },
        )

        result = itn_calculation(df)

        expected = pd.Series([15.0, 22.0], index=dates)
        pd.testing.assert_series_equal(result, expected, check_names=False)

    def test_single_station(self):
        dates = pd.date_range("2024-01-01", periods=3, freq="D")
        df = _make_pivoted(dates, {("tntxm", "Only"): [7.0, 8.0, 9.0]})

        result = itn_calculation(df)

        expected = pd.Series([7.0, 8.0, 9.0], index=dates)
        pd.testing.assert_series_equal(result, expected, check_names=False)


# ── calculate_return_itn ────────────────────────────────────────────


class TestCalculateReturnItn:
    def test_applies_reims_correction_when_both_stations_present(self):
        dates = pd.to_datetime(["2012-05-06", "2012-05-07", "2012-05-08", "2012-05-09"])
        stations_df = pd.DataFrame(
            [
                {"id": REIMS_COURCY_ID, "code": REIMS_COURCY_ID, "nom": "Reims-Courcy"},
                {"id": REIMS_PRUNAY_ID, "code": REIMS_PRUNAY_ID, "nom": "Reims-Prunay"},
                {"id": "75114001", "code": "75114001", "nom": "Paris - Montsouris"},
                {"id": "13054001", "code": "13054001", "nom": "Marseille - Marignane"},
            ]
        )
        temp_daily = pd.DataFrame(
            [
                {
                    "station_id": REIMS_COURCY_ID,
                    "nom": "Reims-Courcy",
                    "date": dates[0],
                    "temp_max": 13.0,
                    "temp_min": 3.0,
                    "tntxm": 8.0,
                },
                {
                    "station_id": REIMS_COURCY_ID,
                    "nom": "Reims-Courcy",
                    "date": dates[1],
                    "temp_max": 14.0,
                    "temp_min": 4.0,
                    "tntxm": 9.0,
                },
                {
                    "station_id": REIMS_COURCY_ID,
                    "nom": "Reims-Courcy",
                    "date": dates[2],
                    "temp_max": 15.0,
                    "temp_min": 5.0,
                    "tntxm": 10.0,
                },
                {
                    "station_id": REIMS_COURCY_ID,
                    "nom": "Reims-Courcy",
                    "date": dates[3],
                    "temp_max": 16.0,
                    "temp_min": 6.0,
                    "tntxm": 11.0,
                },
                {
                    "station_id": REIMS_PRUNAY_ID,
                    "nom": "Reims-Prunay",
                    "date": dates[0],
                    "temp_max": 13.0,
                    "temp_min": 3.0,
                    "tntxm": 8.0,
                },
                {
                    "station_id": REIMS_PRUNAY_ID,
                    "nom": "Reims-Prunay",
                    "date": dates[1],
                    "temp_max": 14.0,
                    "temp_min": 4.0,
                    "tntxm": 9.0,
                },
                {
                    "station_id": REIMS_PRUNAY_ID,
                    "nom": "Reims-Prunay",
                    "date": dates[2],
                    "temp_max": 15.0,
                    "temp_min": 5.0,
                    "tntxm": 10.0,
                },
                {
                    "station_id": REIMS_PRUNAY_ID,
                    "nom": "Reims-Prunay",
                    "date": dates[3],
                    "temp_max": 16.0,
                    "temp_min": 6.0,
                    "tntxm": 11.0,
                },
                {
                    "station_id": "75114001",
                    "nom": "Paris - Montsouris",
                    "date": dates[0],
                    "temp_max": 16.0,
                    "temp_min": 6.0,
                    "tntxm": 11.0,
                },
                {
                    "station_id": "75114001",
                    "nom": "Paris - Montsouris",
                    "date": dates[1],
                    "temp_max": 17.0,
                    "temp_min": 7.0,
                    "tntxm": 12.0,
                },
                {
                    "station_id": "75114001",
                    "nom": "Paris - Montsouris",
                    "date": dates[2],
                    "temp_max": 18.0,
                    "temp_min": 8.0,
                    "tntxm": 13.0,
                },
                {
                    "station_id": "75114001",
                    "nom": "Paris - Montsouris",
                    "date": dates[3],
                    "temp_max": 19.0,
                    "temp_min": 9.0,
                    "tntxm": 14.0,
                },
                {
                    "station_id": "13054001",
                    "nom": "Marseille - Marignane",
                    "date": dates[0],
                    "temp_max": 20.0,
                    "temp_min": 10.0,
                    "tntxm": 15.0,
                },
                {
                    "station_id": "13054001",
                    "nom": "Marseille - Marignane",
                    "date": dates[1],
                    "temp_max": 21.0,
                    "temp_min": 11.0,
                    "tntxm": 16.0,
                },
                {
                    "station_id": "13054001",
                    "nom": "Marseille - Marignane",
                    "date": dates[2],
                    "temp_max": 22.0,
                    "temp_min": 12.0,
                    "tntxm": 17.0,
                },
                {
                    "station_id": "13054001",
                    "nom": "Marseille - Marignane",
                    "date": dates[3],
                    "temp_max": 23.0,
                    "temp_min": 13.0,
                    "tntxm": 18.0,
                },
            ]
        )

        result = calculate_return_itn(
            read_temperatures_gateway=lambda stations_itn: (stations_df, temp_daily)
        )

        # Courcy tntxm=8,9,NaN,NaN  Prunay=NaN,NaN,10,11  Paris=11,12,13,14  Marseille=15,16,17,18
        expected = np.array(
            [
                ["2012-05-06", 34.0 / 3.0],
                ["2012-05-07", 37.0 / 3.0],
                ["2012-05-08", 40.0 / 3.0],
                ["2012-05-09", 43.0 / 3.0],
            ]
        )
        np.testing.assert_array_equal(result[:, 0], expected[:, 0])
        np.testing.assert_allclose(
            result[:, 1].astype(float), expected[:, 1].astype(float)
        )

    def test_no_reims_correction_without_both_stations(self):
        dates = pd.to_datetime(["2024-01-01", "2024-01-02"])
        stations_df = pd.DataFrame(
            [
                {"id": "75114001", "code": "75114001", "nom": "Paris"},
                {"id": "13054001", "code": "13054001", "nom": "Marseille"},
            ]
        )
        temp_daily = pd.DataFrame(
            [
                {
                    "station_id": "75114001",
                    "nom": "Paris",
                    "date": dates[0],
                    "temp_max": 16.0,
                    "temp_min": 6.0,
                    "tntxm": 11.0,
                },
                {
                    "station_id": "75114001",
                    "nom": "Paris",
                    "date": dates[1],
                    "temp_max": 17.0,
                    "temp_min": 7.0,
                    "tntxm": 12.0,
                },
                {
                    "station_id": "13054001",
                    "nom": "Marseille",
                    "date": dates[0],
                    "temp_max": 20.0,
                    "temp_min": 10.0,
                    "tntxm": 15.0,
                },
                {
                    "station_id": "13054001",
                    "nom": "Marseille",
                    "date": dates[1],
                    "temp_max": 21.0,
                    "temp_min": 11.0,
                    "tntxm": 16.0,
                },
            ]
        )
        gateway = _make_gateway(stations_df, temp_daily)

        result = calculate_return_itn(read_temperatures_gateway=gateway)

        expected = np.array(
            [
                ["2024-01-01", 13.0],
                ["2024-01-02", 14.0],
            ]
        )
        np.testing.assert_array_equal(result[:, 0], expected[:, 0])
        np.testing.assert_allclose(
            result[:, 1].astype(float), expected[:, 1].astype(float)
        )

    def test_single_station(self):
        dates = pd.to_datetime(["2024-06-01", "2024-06-02", "2024-06-03"])
        stations_df = pd.DataFrame(
            [
                {"id": "75114001", "code": "75114001", "nom": "Paris"},
            ]
        )
        temp_daily = pd.DataFrame(
            [
                {
                    "station_id": "75114001",
                    "nom": "Paris",
                    "date": dates[0],
                    "temp_max": 20.0,
                    "temp_min": 10.0,
                    "tntxm": 15.0,
                },
                {
                    "station_id": "75114001",
                    "nom": "Paris",
                    "date": dates[1],
                    "temp_max": 22.0,
                    "temp_min": 12.0,
                    "tntxm": 17.0,
                },
                {
                    "station_id": "75114001",
                    "nom": "Paris",
                    "date": dates[2],
                    "temp_max": 24.0,
                    "temp_min": 14.0,
                    "tntxm": 19.0,
                },
            ]
        )
        gateway = _make_gateway(stations_df, temp_daily)

        result = calculate_return_itn(read_temperatures_gateway=gateway)

        expected = np.array(
            [
                ["2024-06-01", 15.0],
                ["2024-06-02", 17.0],
                ["2024-06-03", 19.0],
            ]
        )
        np.testing.assert_array_equal(result[:, 0], expected[:, 0])
        np.testing.assert_allclose(
            result[:, 1].astype(float), expected[:, 1].astype(float)
        )

    def test_default_stations_used_when_none(self):
        received_args = []
        stations_df = pd.DataFrame(
            [
                {"id": "75114001", "code": "75114001", "nom": "Paris"},
            ]
        )
        temp_daily = pd.DataFrame(
            [
                {
                    "station_id": "75114001",
                    "nom": "Paris",
                    "date": pd.Timestamp("2024-01-01"),
                    "temp_max": 10.0,
                    "temp_min": 2.0,
                    "tntxm": 6.0,
                },
            ]
        )

        def spy_gateway(stations_itn=None):
            received_args.append(stations_itn)
            return stations_df, temp_daily

        calculate_return_itn(read_temperatures_gateway=spy_gateway)

        assert received_args[0] == DEFAULT_ITN_STATIONS_LIST
