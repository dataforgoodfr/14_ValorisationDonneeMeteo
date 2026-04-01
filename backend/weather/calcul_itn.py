import datetime
from calendar import monthrange
from collections.abc import Iterable

import numpy as np
import pandas as pd

from weather.itn.gateway import ReadTemperaturesGateway

DEFAULT_ITN_STATIONS_LIST = (
    "06088001",  # Nice - Côte d'Azur
    "13054001",  # Marseille - Marignane
    "14137001",  # Caen - Carpiquet
    "16089001",  # Cognac - Châteaubernard
    "20148001",  # Bastia - Poretta
    "21473001",  # Dijon - Longvic
    "25056001",  # Besançon - Thise
    "26198001",  # Montélimar - Ancone
    "29075001",  # Brest - Guipavas
    "30189001",  # Nîmes - Courbessac
    "31069001",  # Toulouse - Blagnac
    "33281001",  # Bordeaux - Mérignac
    "35281001",  # Rennes - St Jacques
    "36063001",  # Châteauroux - Déols
    "44020001",  # Nantes - Atlantique
    "45055001",  # Orléans - Bricy
    "47091001",  # Agen - La Garenne
    "51183001",  # Reims - Courcy
    "51449002",  # Reims - Prunay
    "54526001",  # Nancy - Essey
    "58160001",  # Nevers - Marzy
    "59343001",  # Lille - Lesquin
    "63113001",  # Clermont-Ferrand - Aulnat
    "64549001",  # Pau - Uzein
    "66136001",  # Perpignan - Rivesaltes
    "67124001",  # Strasbourg - Entzheim
    "69029001",  # Lyon - Bron
    "72181001",  # Le Mans - Arnage
    "73054001",  # Bourg - St-Maurice
    "75114001",  # Paris - Montsouris
    "86027001",  # Poitiers - Biard
)

REIMS_PRUNAY_ID = "51449002"
REIMS_COURCY_ID = "51183001"


# --------------------------------------------------------------------
def separate_by_station(
    df: pd.DataFrame,
    index: str = "",
    columns: str = "",
    values: list[str] | str = "",
    freq: str = "h",
) -> pd.DataFrame:
    """
    Pivot the data to get one column for each meteorological station.

    Parameters
    ----------
    df: pandas.core.frame.DataFrame
          temperature data to pivot
    index: str
          column to use as the new frame's index
    columns: str
          column to use as the new frame's columns
    values: str
          column(s) to use as the new frame's values
    freq: str
          time frequency of the new frame

    Returns
    -------
    pandas.core.frame.DataFrame
          temperature records, with one column per station
    """

    assert (
        (index != "") and (columns != "") and (values != "")
    ), "Cannot pivot, missing arguments"

    data_temp = pd.pivot_table(
        df, index=index, columns=columns, values=values, sort=False
    )

    return data_temp.asfreq(freq).astype(float)


# --------------------------------------------------------------------
def correct_temperatures_Reims(df: pd.DataFrame) -> pd.DataFrame:  # noqa: N802
    """
    The ITN calculation will use the data of the Reims-Courcy station
    until 07/05/2012, and the Reims-Prunay station starting from 08/05/2012.
    See the discussion of issue #25 in GitHub for more details.

    Not tested because the data are not modelled.

    Parameters
    ----------
    pandas.core.frame.DataFrame
          temperature records, with one column per station

    Returns
    -------
    pandas.core.frame.DataFrame
          temperature records, with one column per station that include
          correction for the Reims-Prunay station.
    """

    # Reims-Prunay: keep only the data after Reims-Courcy was decommissioned
    corrected_df = df.copy()
    indexes = corrected_df.columns
    for index in indexes:
        if REIMS_COURCY_ID in index:
            corrected_df.loc["2012-05-08":, index] = float("nan")
        elif REIMS_PRUNAY_ID in index:
            corrected_df.loc[:"2012-05-07", index] = float("nan")

    return corrected_df


# --------------------------------------------------------------------
def itn_calculation(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract only the temperature records and create on column for each station.

    Parameters
    ----------
    pandas.core.frame.DataFrame
          daily temperature records, with one column per station

    Returns
    -------
    pandas.core.frame.DataFrame
          computed ITN following the method of InfoClimat
    """

    temp_mean = df["tntxm"]

    return temp_mean.mean(axis=1)


# --------------------------------------------------------------------
def compute_itn(
    read_protocol: ReadTemperaturesGateway,
    stations_itn: Iterable | None = None,
    start_date: str | pd.Timestamp | datetime.datetime | None = None,
    end_date: str | pd.Timestamp | datetime.datetime | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Main part of the ITN computation. Return the daily records by stations
    and the ITN in pandas DataFrames format.

    Parameters
    ----------
    read_protocol: ReadTemperaturesGateway
          protocol used to read the data
    stations_itn: Iterable
          list of the unique ID of the meteorological stations to be
          considered to calculate the ITN.
    start_date: str or pd.Timestamp or datetime.datetime
          beginning of the time period to consider
    end_date: str or pd.Timestamp or datetime.datetime
          end of the time period to consider

    Returns
    -------
    daily_records_by_station(_corr): pd.DataFrame
          temperature records, with one column per station
    itn: pd.DataFrame
          daily ITN
    """

    stations, temp_daily = read_protocol.read_temperatures(
        stations_itn, start_date, end_date
    )

    daily_records_by_station = separate_by_station(
        temp_daily,
        index="date",
        columns="station_id",
        values=["temp_min", "temp_max", "tntxm"],
        freq="D",
    )

    if (REIMS_COURCY_ID in stations["id"].values) and (
        REIMS_PRUNAY_ID in stations["id"].values
    ):
        daily_records_by_station_corr = correct_temperatures_Reims(
            daily_records_by_station
        )
        itn = itn_calculation(daily_records_by_station_corr)

        return daily_records_by_station_corr, itn
    else:
        itn = itn_calculation(daily_records_by_station)

        return daily_records_by_station, itn


# --------------------------------------------------------------------
def average_itn_calculation(
    read_protocol: ReadTemperaturesGateway,
    stations_itn: Iterable | None = None,
    start_date: str | pd.Timestamp | datetime.datetime | None = None,
    end_date: str | pd.Timestamp | datetime.datetime | None = None,
    freq: str = "monthly",
) -> pd.DataFrame:
    """
    Calculate the monthly or yearly ITN by taking the average of
    the daily ITN. To improve the precision of the output value,
    we average the daily minimum and maximum temperatures for
    the 30 stations and average everything at once.

    Parameters
    ----------
    read_protocol: ReadTemperaturesGateway
          protocol used to read the data
    stations_itn: tuple of str
        the unique ID of the meteorological stations that are used to
        calculate the ITN
    start_date: str or pd.Timestamp or datetime.datetime
          beginning of the time period to consider
    end_date: str or pd.Timestamp or datetime.datetime
          end of the time period to consider
    freq: str
        specify whether to calculate the monthly or yearly ITN

    Returns
    -------
    pandas.core.frame.DataFrame
          computed monthly or yealry ITN
    """
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

    return avg_itn


# --------------------------------------------------------------------
def itn(
    *,
    read_protocol: ReadTemperaturesGateway,
    stations_itn: Iterable | None = None,
    start_date: str | pd.Timestamp | datetime.datetime | None = None,
    end_date: str | pd.Timestamp | datetime.datetime | None = None,
) -> np.array:
    """
    Export the ITN in an array.

    Parameters
    ----------
    read_protocol: ReadTemperaturesGateway
          protocol used to read the data
    stations_itn: Iterable
          list of the unique ID of the meteorological stations to be
          considered to calculate the ITN.
    start_date: str or pd.Timestamp or datetime.datetime
          beginning of the time period to consider
    end_date: str or pd.Timestamp or datetime.datetime
          end of the time period to consider

    Returns
    -------
    numpy.ndarray
          array Nx2 containing the date and ITN
    """

    # by default, calculate ITN for France
    if stations_itn is None:
        stations_itn = DEFAULT_ITN_STATIONS_LIST

    itn = compute_itn(read_protocol, stations_itn, start_date, end_date)[1]

    dates = itn.index.strftime("%Y-%m-%d").to_numpy()
    values = itn.values

    return np.array(list(zip(dates, values, strict=True)))


# --------------------------------------------------------------------
def monthly_itn(
    *,
    read_protocol: ReadTemperaturesGateway,
    stations_itn: Iterable | None = None,
    start_date: str | pd.Timestamp | datetime.datetime | None = None,
    end_date: str | pd.Timestamp | datetime.datetime | None = None,
) -> np.array:
    """
    Export the monthly ITN in an array.

    Parameters
    ----------
    read_protocol: ReadTemperaturesGateway
          protocol used to read the data
    stations_itn: Iterable
          list of the unique ID of the meteorological stations to be
          considered to calculate the ITN.
    start_date: str or pd.Timestamp or datetime.datetime
          beginning of the time period to consider
    end_date: str or pd.Timestamp or datetime.datetime
          end of the time period to consider

    Returns
    -------
    numpy.ndarray
          array Nx2 containing the date and ITN
    """

    # by default, calculate ITN for France
    if stations_itn is None:
        stations_itn = DEFAULT_ITN_STATIONS_LIST

    if (type(start_date) is str) and (start_date is not None):
        tmp = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        start_date = datetime.datetime(tmp.year, tmp.month, 1)
    elif start_date is not None:
        start_date = start_date.replace(day=1)

    if (type(end_date) is str) and (end_date is not None):
        tmp = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        last_day = monthrange(tmp.year, tmp.month)[1]
        end_date = datetime.datetime(tmp.year, tmp.month, last_day)
    elif end_date is not None:
        last_day = monthrange(end_date.year, end_date.month)[1]
        end_date = end_date.replace(day=last_day)

    itn = average_itn_calculation(
        read_protocol, stations_itn, start_date, end_date, freq="monthly"
    )

    dates = itn.index.to_numpy()
    values = itn["avg_itn"].values

    return np.array(list(zip(dates, values, strict=True)))


# --------------------------------------------------------------------
def annual_itn(
    *,
    read_protocol: ReadTemperaturesGateway,
    stations_itn: Iterable | None = None,
    start_date: str | pd.Timestamp | datetime.datetime | None = None,
    end_date: str | pd.Timestamp | datetime.datetime | None = None,
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
    start_date: str or pd.Timestamp or datetime.datetime
          beginning of the time period to consider
    end_date: str or pd.Timestamp or datetime.datetime
          end of the time period to consider

    Returns
    -------
    numpy.ndarray
          array Nx2 containing the date and ITN
    """

    # by default, calculate ITN for France
    if stations_itn is None:
        stations_itn = DEFAULT_ITN_STATIONS_LIST

    if (type(start_date) is str) and (start_date is not None):
        tmp = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        start_date = datetime.datetime(tmp.year, 1, 1)
    elif start_date is not None:
        start_date = start_date.replace(month=1, day=1)

    if (type(end_date) is str) and (end_date is not None):
        tmp = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        end_date = datetime.datetime(tmp.year, 12, 31)
    elif end_date is not None:
        end_date = end_date.replace(month=12, day=31)

    itn = average_itn_calculation(
        read_protocol, stations_itn, start_date, end_date, freq="yearly"
    )

    dates = itn.index.to_numpy()
    values = itn["avg_itn"].values

    return np.array(list(zip(dates, values, strict=True)))


# --------------------------------------------------------------------
