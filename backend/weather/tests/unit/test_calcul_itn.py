import pandas as pd
import pytest

from weather.calcul_itn import (
    separate_by_station,
)


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
