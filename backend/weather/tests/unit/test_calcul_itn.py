import pandas as pd
import pytest

from weather.calcul_itn import (
    correct_temperatures_Reims,
    # DEFAULT_ITN_STATIONS_LIST,
    # REIMS_COURCY_ID,
    # REIMS_PRUNAY_ID,
    # calculate_return_itn,
    itn_calculation,
    separate_by_station,
)

NAN = float("nan")


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
    df.columns = pd.MultiIndex.from_tuples(df.columns, names=[None, "nom"])
    return df


# == separate_by_station =============================================


def test_separate_by_station():
    dates = pd.date_range("2024-01-01", periods=2, freq="D")
    df = pd.DataFrame(
        {
            "date": [dates[0], dates[1], dates[0], dates[1]],
            "nom": ["A", "A", "B", "B"],
            "tn": [4.0, 5.0, 14.0, 15.0],
            "tx": [6.0, 9.0, 16.0, 19.0],
            "tntxm": [5.0, 7.0, 15.0, 17.0],
        }
    )

    result = separate_by_station(
        df, index="date", columns="nom", values=["tntxm"], freq="D"
    )
    expected = _make_pivoted(
        dates,
        {
            ("tntxm", "A"): [5.0, 7.0],
            ("tntxm", "B"): [15.0, 17.0],
        },
    )
    pd.testing.assert_frame_equal(result, expected)

    result = separate_by_station(
        df, index="date", columns="nom", values=["tn", "tntxm"], freq="D"
    )
    expected = _make_pivoted(
        dates,
        {
            ("tn", "A"): [4.0, 5.0],
            ("tn", "B"): [14.0, 15.0],
            ("tntxm", "A"): [5.0, 7.0],
            ("tntxm", "B"): [15.0, 17.0],
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


def test_correct_temperatures_Reims():
    dates = pd.date_range("2012-05-06", "2012-05-09", freq="D")
    input_df = _make_pivoted(
        dates,
        {
            ("tntxm", "Reims-Courcy"): [8.0, 9.0, 10.0, 11.0],
            ("tntxm", "Reims-Prunay"): [18.0, 19.0, 20.0, 21.0],
            ("tntxm", "Paris"): [11.0, 12.0, 13.0, 14.0],
        },
    )
    original = input_df.copy()

    result = correct_temperatures_Reims(input_df)
    expected = _make_pivoted(
        dates,
        {
            ("tntxm", "Reims-Courcy"): [8.0, 9.0, NAN, NAN],
            ("tntxm", "Reims-Prunay"): [NAN, NAN, 20.0, 21.0],
            ("tntxm", "Paris"): [11.0, 12.0, 13.0, 14.0],
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
            ("tntxm", "A"): [10.0, 12.0, 14.0, 16.0],
            ("tntxm", "B"): [20.0, 22.0, 24.0, 26.0],
        },
    )
    result = itn_calculation(df)
    expected = pd.Series([15.0, 17.0, 19.0, 21.0], index=dates)
    pd.testing.assert_series_equal(result, expected, check_names=False)

    df = _make_pivoted(
        dates,
        {
            ("tntxm", "A"): [10.0, NAN, 14.0, 16.0],
            ("tntxm", "B"): [20.0, 22.0, 24.0, NAN],
        },
    )
    result = itn_calculation(df)
    expected = pd.Series([15.0, 22.0, 19.0, 16.0], index=dates)
    pd.testing.assert_series_equal(result, expected, check_names=False)

    df = _make_pivoted(
        dates,
        {
            ("tntxm", "A"): [10.0, 12.0, 14.0, 16.0],
        },
    )
    result = itn_calculation(df)
    expected = pd.Series([10.0, 12.0, 14.0, 16.0], index=dates)
    pd.testing.assert_series_equal(result, expected, check_names=False)
