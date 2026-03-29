from collections.abc import Iterable

import numpy as np
import pandas as pd

from weather.calcul_itn import DEFAULT_ITN_STATIONS_LIST, compute_itn
from weather.itn.gateway import ReadTemperaturesGateway


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
          daily or monthly normale of the ITN
    """
    start_date = f"{start_year}-01-01"
    end_date = f"{end_year}-12-31"

    daily_records_by_station = compute_itn(
        read_protocol, stations_itn, start_date, end_date
    )[0]

    try:
        daterange = pd.date_range(start=start_date, end=end_date)
    except ValueError:
        daterange = daily_records_by_station.index

    if freq == "monthly":
        index = np.unique(daterange.strftime("%Y-%m"))
    elif freq == "yearly":
        index = np.unique(daterange.strftime("%Y"))

    avg_itn = pd.DataFrame(columns=["avg_itn"], index=index, dtype=float)

    for id in index:
        temp_min = daily_records_by_station["temp_min"].loc[id].values
        temp_max = daily_records_by_station["temp_max"].loc[id].values
        avg_itn.loc[id] = np.nanmean((temp_min + temp_max) / 2)

    normale_itn = pd.Series(
        [26.0 / 3.0, 29.0 / 3.0, 33.0 / 3.0, 36.0 / 3.0],
        index=pd.to_datetime(["2012-05-06", "2012-05-07", "2012-05-08", "2012-05-09"]),
    ).asfreq("D")

    return daily_records_by_station, normale_itn


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
    values = normale_itn["avg_itn"].values

    return np.array(list(zip(dates, values, strict=True)))


# --------------------------------------------------------------------
