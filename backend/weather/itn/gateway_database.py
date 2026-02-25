import os
from collections.abc import Iterable

import pandas as pd
from django.db import connection

COLUMN_NAME_INDEX = 0

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
        {
            columns[index][COLUMN_NAME_INDEX]: column
            for index, column in enumerate(value)
        }
        for value in cursor.fetchall()
    ]

    return pd.DataFrame(result)


# --------------------------------------------------------------------
def read_temperatures_using_database(
    stations_itn: Iterable | None = None,
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
    temp_daily: pandas.core.frame.DataFrame
          daily record of the min, max and 'mean' temperature
    """

    sql_request = """SELECT
                       id,
                       code,
                       nom
                    FROM
                       weather_station
                 """
    if stations_itn is None:
        stations_itn = ()

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
