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
                        w.date,
                        w.tx as temp_max,
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
    The ITN calculation will use the data of the Reims-Courcy station
    until 07/05/2012, and the Reims-Prunayc station starting from 08/05/2012.
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
def calculate_return_itn(stations_itn: tuple[str] = ()) -> np.array:
    """
    Main part of the script.

    Parameters
    ----------
    list or tuple
          list of the stations to be considered to calculate the ITN.

    Returns
    -------
    numpy.ndarray
          array Nx2 containing the date and ITN
    """

    # by default, calculate ITN for France
    if len(stations_itn) == 0:
        stations_itn = (
            "6088001",  # Nice - Côte d'Azur
            # "06088001" ?
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
