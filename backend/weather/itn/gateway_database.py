import datetime
import os
from collections.abc import Iterable

import pandas as pd
from django.db import connection

COLUMN_NAME_INDEX = 0

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")


class ReadTemperaturesDatabase:
    def sql2pandas(self, sql_request: str) -> pd.DataFrame:
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

    def read_temperatures(
        self,
        stations_itn: Iterable | None = None,
        start_date: str | pd.Timestamp | datetime.datetime | None = None,
        end_date: str | pd.Timestamp | datetime.datetime | None = None,
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Define the SQL request to extract the data from the database, consult the database and
        return the results as pandas DataFrames. The times are converted into datetime object.

        Parameters
        ----------
        stations_itn: Iterable
              list of the unique ID of the meteorological stations to be
              considered to calculate the ITN.
        start_date: str or pd.Timestamp or datetime.datetime
              beginning of the time period to consider
        end_date: str or pd.Timestamp or datetime.datetime
              end of the time period to consider

        Returns
        -------
        stations: pandas.core.frame.DataFrame
              data of the stations extracted
        temp_daily: pandas.core.frame.DataFrame
              daily record of the min, max and 'mean' temperature
        """
        sql_request = """SELECT station_code as id,
                                station_code as code,
                                name as nom
                         FROM v_station
                      """
        if stations_itn is not None:
            sql_request += f"""WHERE
                                station_code in {stations_itn}"""
        stations = self.sql2pandas(sql_request)

        sql_request = f"""SELECT
                            \"NUM_POSTE\" as station_id,
                            \"AAAAMMJJ\" as date,
                            \"TX\" as temp_max,
                            \"TN\" as temp_min,
                            \"TNTXM\" as tntxm
                         FROM
                            \"Quotidienne\"
                         WHERE
                            \"NUM_POSTE\" in {tuple(stations["id"])}
                     """
        if (start_date is not None) and (end_date is not None):
            sql_request += (
                f"and '{start_date}' <= \"AAAAMMJJ\" and \"AAAAMMJJ\" <= '{end_date}' "
            )
        elif start_date is not None:
            sql_request += f"and \"AAAAMMJJ\" >= '{start_date}' "
        elif end_date is not None:
            sql_request += f"and \"AAAAMMJJ\" <= '{end_date}' "
        temp_daily = self.sql2pandas(sql_request)
        temp_daily["date"] = pd.to_datetime(temp_daily["date"])

        return stations, temp_daily
