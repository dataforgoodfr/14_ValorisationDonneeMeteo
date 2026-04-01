import calendar
from collections.abc import Iterable

import numpy as np
import pandas as pd

from weather.calcul_itn import DEFAULT_ITN_STATIONS_LIST, compute_itn
from weather.itn.gateway import ReadTemperaturesGateway

NAN = float("nan")


# --------------------------------------------------------------------
def add_simulate_29th_february(
    df: pd.DataFrame, start_year: int = 1991, end_year: int = 2020
) -> pd.DataFrame:
    """
    For the non-leap year, add a simulated 29th February in order to derive
    the daily normale. This simulated day is the average of 28th February
    and 1st March.

    Parameters
    ----------
    df: pd.DataFrame
          input data
    start_year: int
          beginning of the period to calculate the normale
    end_year: int
          end of the period to calculate the normale

    Returns
    -------
    pd.DataFrame
          data with the simulated 29th February
    """
    new_df = df.copy()
    new_df.index = new_df.index.strftime("%Y-%m-%d")

    for year in range(start_year, end_year + 1, 1):
        if not calendar.isleap(year):
            new_df.loc[f"{year}-02-29"] = np.mean(
                [new_df[f"{year}-02-28"], new_df[f"{year}-03-01"]]
            )

    return new_df


# --------------------------------------------------------------------
def compute_normale_itn(
    read_protocol: ReadTemperaturesGateway,
    stations_itn: Iterable | None = None,
    start_year: int = 1991,
    end_year: int = 2020,
    freq: str = "daily",
) -> pd.DataFrame:
    """
    Derive the daily/monthly normale of the ITN and return it in pandas DataFrame format.

    Parameters
    ----------
    read_protocol: ReadTemperaturesGateway
          protocol used to read the data
    stations_itn: Iterable
          list of the unique ID of the meteorological stations to be
          considered to calculate the ITN.
    start_year: int
          beginning of the period to calculate the normale
    end_year: int
          end of the period to calculate the normale
    freq: str
        specify whether to calculate the daily or monthly normale of the ITN

    Returns
    -------
    pd.DataFrame
          daily, monthly or yearly normale of the ITN
    """
    start_date = f"{start_year}-01-01"
    end_date = f"{end_year}-12-31"

    itn = compute_itn(read_protocol, stations_itn, start_date, end_date)[1]

    if freq == "daily":
        index = pd.date_range(start="2024-01-01", end="2024-12-31", freq="D")
        normale = pd.DataFrame(columns=["normale"], index=index, dtype=float)

        new_itn = add_simulate_29th_february(
            itn, start_year=start_year, end_year=end_year
        )
        for date in index:
            normale.loc[date.strftime("%Y-%m-%d")] = new_itn[
                new_itn.index.str.contains(date.strftime("-%m-%d"))
            ].mean()
        normale.index = normale.index.strftime("%d-%b")
    elif freq == "monthly":
        index = pd.date_range(start="2024-01-01", periods=12, freq="ME").strftime("%b")
        normale = pd.DataFrame(columns=["normale"], index=index, dtype=float)
        for month in index:
            normale.loc[month] = itn[itn.index.strftime("%b") == month].mean()
    elif freq == "yearly":
        normale = pd.DataFrame(
            {"normale": [itn.mean()]}, index=[f"{start_year}-{end_year}"]
        )

    return normale


# --------------------------------------------------------------------
def normale_itn(
    *,
    read_protocol: ReadTemperaturesGateway,
    stations_itn: Iterable | None = None,
    start_year: int = 1991,
    end_year: int = 2020,
    freq: str = "daily",
) -> np.array:
    """
    Export the annual ITN in an array.

    Parameters
    ----------
    read_protocol: ReadTemperaturesGateway
          protocol used to read the data
    stations_itn: Iterable
          list of the unique ID of the meteorological stations to be
          considered to calculate the ITN.
    start_year: int
          beginning of the period to calculate the normale
    end_year: int
          end of the period to calculate the normale
    freq: str
        specify whether to calculate the daily or monthly normale of the ITN

    Returns
    -------
    numpy.ndarray
          array Nx2 containing the date and the daily/monthly normale of the ITN
    """

    # by default, calculate ITN for France
    if stations_itn is None:
        stations_itn = DEFAULT_ITN_STATIONS_LIST

    normale_itn = compute_normale_itn(
        read_protocol, stations_itn, start_year, end_year, freq
    )

    dates = normale_itn.index.to_numpy()
    values = normale_itn["normale"].values

    return np.array(list(zip(dates, values, strict=True)))


# --------------------------------------------------------------------
