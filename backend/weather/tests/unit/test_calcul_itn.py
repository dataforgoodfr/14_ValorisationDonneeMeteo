import numpy as np
import pandas as pd
import pytest

from weather.calcul_itn import (
    annual_itn,
    average_itn_calculation,
    compute_itn,
    correct_temperatures_Reims,
    itn,
    itn_calculation,
    monthly_itn,
    separate_by_station,
)
from weather.itn.gateway_tests import (
    ReadMonthlyTemperaturesTests,
    ReadTemperaturesTests,
    ReadYearlyTemperaturesTests,
)

NAN = float("nan")
REIMS_PRUNAY_ID = "51449002"
REIMS_COURCY_ID = "51183001"


def _make_pivoted(index, columns_data):
    """
    Build a pivoted DataFrame matching the shape of separate_by_station output.

    Parameters
    ----------
    index: pandas.DatetimeIndex
          column to use as the new frame's index
    columns_data: dict
        (metric, station_name) → list of values.

    Returns
    -------
    pandas.core.frame.DataFrame
          pivoted matching the shape of separate_by_station output
    """
    df = pd.DataFrame(columns_data, index=index)
    df.index.name = "date"
    df.columns = pd.MultiIndex.from_tuples(df.columns, names=[None, "station_id"])
    return df


# == separate_by_station =============================================


def test_separate_by_station():
    dates = pd.date_range("2024-01-01", periods=2, freq="D")
    df = pd.DataFrame(
        {
            "date": [dates[0], dates[1], dates[0], dates[1]],
            "station_id": ["75114001", "75114001", "13054001", "13054001"],
            "nom": ["A", "A", "B", "B"],
            "tn": [4.0, 5.0, 14.0, 15.0],
            "tx": [6.0, 9.0, 16.0, 19.0],
            "tntxm": [5.0, 7.0, 15.0, 17.0],
        }
    )

    result = separate_by_station(
        df, index="date", columns="station_id", values=["tntxm"], freq="D"
    )
    expected = _make_pivoted(
        dates,
        {
            ("tntxm", "75114001"): [5.0, 7.0],
            ("tntxm", "13054001"): [15.0, 17.0],
        },
    )
    pd.testing.assert_frame_equal(result, expected)

    result = separate_by_station(
        df, index="date", columns="station_id", values=["tn", "tntxm"], freq="D"
    )
    expected = _make_pivoted(
        dates,
        {
            ("tn", "75114001"): [4.0, 5.0],
            ("tn", "13054001"): [14.0, 15.0],
            ("tntxm", "75114001"): [5.0, 7.0],
            ("tntxm", "13054001"): [15.0, 17.0],
        },
    )
    pd.testing.assert_frame_equal(result, expected)

    with pytest.raises(AssertionError, match="Cannot pivot, missing arguments"):
        separate_by_station(df, index="", columns="a", values=["a"])

    with pytest.raises(AssertionError, match="Cannot pivot, missing arguments"):
        separate_by_station(df, index="a", columns="", values=["a"])

    with pytest.raises(AssertionError, match="Cannot pivot, missing arguments"):
        separate_by_station(df, index="a", columns="a", values="")


# == correct_temperatures_Reims ======================================


def test_correct_temperatures_Reims():  # noqa: N802
    dates = pd.date_range("2012-05-06", "2012-05-09", freq="D")
    input_df = _make_pivoted(
        dates,
        {
            ("tntxm", REIMS_COURCY_ID): [8.0, 9.0, 10.0, 11.0],
            ("tntxm", REIMS_PRUNAY_ID): [18.0, 19.0, 20.0, 21.0],
            ("tntxm", "75114001"): [11.0, 12.0, 13.0, 14.0],
        },
    )
    original = input_df.copy()

    result = correct_temperatures_Reims(input_df)
    expected = _make_pivoted(
        dates,
        {
            ("tntxm", REIMS_COURCY_ID): [8.0, 9.0, NAN, NAN],
            ("tntxm", REIMS_PRUNAY_ID): [NAN, NAN, 20.0, 21.0],
            ("tntxm", "75114001"): [11.0, 12.0, 13.0, 14.0],
        },
    )
    pd.testing.assert_frame_equal(result, expected)

    correct_temperatures_Reims(input_df)
    pd.testing.assert_frame_equal(input_df, original)


# == itn_calculation =================================================


def test_itn_calculation():
    dates = pd.date_range("2024-01-01", periods=4, freq="D")

    df = _make_pivoted(
        dates,
        {
            ("tntxm", "75114001"): [10.0, 12.0, 14.0, 16.0],
            ("tntxm", "13054001"): [20.0, 22.0, 24.0, 26.0],
        },
    )
    result = itn_calculation(df)
    expected = pd.Series([15.0, 17.0, 19.0, 21.0], index=dates)
    pd.testing.assert_series_equal(result, expected, check_names=False)

    df = _make_pivoted(
        dates,
        {
            ("tntxm", "75114001"): [10.0, NAN, 14.0, 16.0],
            ("tntxm", "13054001"): [20.0, 22.0, 24.0, NAN],
        },
    )
    result = itn_calculation(df)
    expected = pd.Series([15.0, 22.0, 19.0, 16.0], index=dates)
    pd.testing.assert_series_equal(result, expected, check_names=False)

    df = _make_pivoted(
        dates,
        {
            ("tntxm", "75114001"): [10.0, 12.0, 14.0, 16.0],
        },
    )
    result = itn_calculation(df)
    expected = pd.Series([10.0, 12.0, 14.0, 16.0], index=dates)
    pd.testing.assert_series_equal(result, expected, check_names=False)


# == compute_itn =====================================================


def test_compute_itn():
    dates = pd.to_datetime(["2012-05-06", "2012-05-07", "2012-05-08", "2012-05-09"])
    results = compute_itn(ReadTemperaturesTests)
    # Courcy tntxm=8,9,NaN,NaN  Prunay=NaN,NaN,11,12  Paris=3,4,5,6  Marseille=15,16,17,18
    expected_records_by_station = _make_pivoted(
        dates,
        {
            ("temp_min", REIMS_COURCY_ID): [3.0, 4.0, NAN, NAN],
            ("temp_min", REIMS_PRUNAY_ID): [NAN, NAN, 6.0, 7.0],
            ("temp_min", "75114001"): [-2.0, -1.0, 0.0, 1.0],
            ("temp_min", "13054001"): [10.0, 11.0, 12.0, 13.0],
            ("temp_max", REIMS_COURCY_ID): [13.0, 14.0, NAN, NAN],
            ("temp_max", REIMS_PRUNAY_ID): [NAN, NAN, 16.0, 17.0],
            ("temp_max", "75114001"): [8.0, 9.0, 10.0, 11.0],
            ("temp_max", "13054001"): [20.0, 21.0, 22.0, 23.0],
            ("tntxm", REIMS_COURCY_ID): [8.0, 9.0, NAN, NAN],
            ("tntxm", REIMS_PRUNAY_ID): [NAN, NAN, 11.0, 12.0],
            ("tntxm", "75114001"): [3.0, 4.0, 5.0, 6.0],
            ("tntxm", "13054001"): [15.0, 16.0, 17.0, 18.0],
        },
    ).asfreq("D")
    expected_itn = pd.Series(
        [26.0 / 3.0, 29.0 / 3.0, 33.0 / 3.0, 36.0 / 3.0], index=dates
    ).asfreq("D")
    pd.testing.assert_frame_equal(results[0], expected_records_by_station)
    pd.testing.assert_series_equal(results[1], expected_itn)


# == average_itn_calculation =========================================


def test_average_itn_calculation():
    dates = pd.date_range("2024-01-01", "2024-03-31", freq="D")
    index = np.unique(dates.strftime("%Y-%m"))

    results = average_itn_calculation(
        read_protocol=ReadMonthlyTemperaturesTests, freq="monthly"
    )
    expected_avg_itn = pd.DataFrame(
        {"avg_itn": [(11 + 3 + 17) / 3.0 for idx in index]}, index=index
    )
    pd.testing.assert_frame_equal(results, expected_avg_itn)

    dates = pd.date_range("2021-01-01", "2023-12-31", freq="D")
    index = np.unique(dates.strftime("%Y"))

    results = average_itn_calculation(
        read_protocol=ReadYearlyTemperaturesTests, freq="yearly"
    )
    expected_avg_itn = pd.DataFrame(
        {"avg_itn": [(14 - 1 + 21) / 3.0 for idx in index]}, index=index
    )
    pd.testing.assert_frame_equal(results, expected_avg_itn)


# == itn =============================================================


def test_itn():
    result = itn(read_protocol=ReadTemperaturesTests)
    expected = np.array(
        [
            ["2012-05-06", 26.0 / 3.0],
            ["2012-05-07", 29.0 / 3.0],
            ["2012-05-08", 33.0 / 3.0],
            ["2012-05-09", 36.0 / 3.0],
        ]
    )
    np.testing.assert_array_equal(result[:, 0], expected[:, 0])
    np.testing.assert_allclose(result[:, 1].astype(float), expected[:, 1].astype(float))


# == monthly_itn =====================================================


def test_monthly_itn():
    dates = pd.date_range("2024-01-01", "2024-03-31", freq="D")
    index = np.unique(dates.strftime("%Y-%m"))

    result = monthly_itn(read_protocol=ReadMonthlyTemperaturesTests)
    avg_itn = [(11 + 3 + 17) / 3.0 for idx in index]
    expected = np.array([[index[i], avg_itn[i]] for i in range(len(index))])

    np.testing.assert_array_equal(result[:, 0], expected[:, 0])
    np.testing.assert_allclose(result[:, 1].astype(float), expected[:, 1].astype(float))


# == annual_itn =====================================================


def test_annual_itn():
    dates = pd.date_range("2021-01-01", "2023-12-31", freq="D")
    index = np.unique(dates.strftime("%Y"))

    result = annual_itn(read_protocol=ReadYearlyTemperaturesTests)
    avg_itn = [(14 - 1 + 21) / 3.0 for idx in index]
    expected = np.array([[index[i], avg_itn[i]] for i in range(len(index))])

    np.testing.assert_array_equal(result[:, 0], expected[:, 0])
    np.testing.assert_allclose(result[:, 1].astype(float), expected[:, 1].astype(float))
