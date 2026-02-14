import os
from collections.abc import Iterable

import numpy as np
import pandas as pd
from django.db import connection

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")


# --------------------------------------------------------------------
def sql2pandas(sql_request: str) -> pd.DataFrame:
    """
    Given a SQL request, use a cursor to extract the data and convert
    them into a pandas dataframe.

    Parameters
    ----------
    str
          SQL request to extract the data

    Returns
    -------
    pandas.core.frame.DataFrame
          requested data
    """

    cursor = connection.cursor()
    cursor.execute(sql_request)

    columns = cursor.description
    result = [
        {columns[index][0]: column for index, column in enumerate(value)}
        for value in cursor.fetchall()
    ]

    return pd.DataFrame(result)


# --------------------------------------------------------------------
def read_temperatures(
    stations_itn: Iterable = [],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Read the csv file containing the data into a pandas DataFrame. The times
    are converted into datetime object.

    Parameters
    ----------
    list or tuple
          list of the stations to be considered to calculate the ITN.

    Returns
    -------
    stations: pandas.core.frame.DataFrame
          data of the stations extracted
    temp_hourly: pandas.core.frame.DataFrame
          hourly measurement of the air, min and max temperature
    temp_daily: pandas.core.frame.DataFrame
          daily record of the min, max and 'mean' temperature
    """

    sql_request = """SELECT
                       *
                    FROM
                       weather_station
                 """
    if len(stations_itn) > 0:
        sql_request += f"""WHERE
                            code in {stations_itn}"""
    stations = sql2pandas(sql_request)

    sql_request = f"""SELECT
                        w.station_id,
                        w.nom_usuel as nom,
                        w.date, w.tx as temp_max,
                        w.tn as temp_min,
                        w.tntxm as tntxm
                     FROM
                        weather_quotidienne as w
                     WHERE
                        w.station_id in {tuple(stations["id"])}
                 """
    temp_daily = sql2pandas(sql_request)
    temp_daily["date"] = pd.to_datetime(temp_daily["date"])

    return stations, temp_daily


# --------------------------------------------------------------------
def separate_by_station(
    df: pd.DataFrame,
    index: str = "",
    columns: str = "",
    values: str = "",
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
        (index != "") & (columns != "") & (values != "")
    ), "Cannot pivot, missing arguments"

    data_temp = pd.pivot_table(df, index=index, columns=columns, values=values)

    return data_temp.asfreq(freq).astype(float)


# --------------------------------------------------------------------
def correct_temperatures_Reims(df: pd.DataFrame) -> pd.DataFrame:
    """
    Correct the temperatures of the Reims-Prunay station due to the location
    difference with the former Reims-Courcy station.
    This fonction might be updated in the future if a better correction
    is find (discussion in issue #25 of GitHub).

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
        if "Reims-Courcy" in index:
            corrected_df.loc["2012-05-08":, index] = float("nan")
        elif "Reims-Prunay" in index:
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
def calculate_return_itn() -> np.array:
    """
    Main part of the script.

    Parameters
    ----------

    Returns
    -------
    numpy.ndarray
          array Nx2 containing the date and ITN
    """

    stations_itn = (
        "6088001",
        "13054001",
        "14137001",
        "16089001",
        "20148001",
        "21473001",
        "25056001",  # Besançon - Thise?
        "26198001",
        "29075001",
        "30189001",
        "31069001",
        "33281001",
        "35281001",
        "36063001",
        "44020001",
        "45055001",
        "47091001",
        "51449002",  # Reims - Prunay
        "51183001",  # Reims - Courcy
        "54526001",
        "58160001",
        "59343001",
        "63113001",
        "64549001",
        "66164002",  # Perpignan - Rivesaltes?
        "67124001",
        "69029001",
        "72008001",
        "73054001",
        "75114001",
        "86027001",
    )

    stations, temp_daily = read_temperatures(stations_itn)

    daily_records_by_station = separate_by_station(
        temp_daily,
        index="date",
        columns="nom",
        values=["temp_min", "temp_max", "tntxm"],
        freq="D",
    )

    if ("Reims-Courcy" in stations["nom"]) and ("Reims-Prunay" in stations["nom"]):
        daily_records_by_station_corr = correct_temperatures_Reims(
            daily_records_by_station
        )
        itn = itn_calculation(daily_records_by_station_corr)
    else:
        itn = itn_calculation(daily_records_by_station)

    dates = itn.index.strftime("%Y-%m-%d").to_numpy()
    values = itn.values

    return np.array(list(zip(dates, values, strict=True)))


# --------------------------------------------------------------------


# results = calculate_return_itn()
# print(results)

# exec(open('weather/calcul_itn.py').read())
