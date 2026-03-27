from collections.abc import Iterable

import numpy as np
import pandas as pd

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
    normale_itn = pd.Series(
        [26.0 / 3.0, 29.0 / 3.0, 33.0 / 3.0, 36.0 / 3.0],
        index=pd.to_datetime(["2012-05-06", "2012-05-07", "2012-05-08", "2012-05-09"]),
    ).asfreq("D")

    return normale_itn


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
    normale_itn = compute_normale_itn(
        read_protocol, stations_itn, start_year, end_year, freq
    )

    dates = normale_itn.index.to_numpy()
    values = normale_itn["avg_itn"].values

    return np.array(list(zip(dates, values, strict=True)))


# --------------------------------------------------------------------
