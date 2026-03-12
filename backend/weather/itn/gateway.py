import datetime
from collections.abc import Iterable
from typing import Protocol

import pandas as pd


class ReadTemperaturesGateway(Protocol):
    """
    A Protocol reading the temperatures used to compute the ITN.
    """

    def read_temperatures(
        self,
        stations_itn: Iterable | None = None,
        start_date: str | pd.Timestamp | datetime.datetime | None = None,
        end_date: str | pd.Timestamp | datetime.datetime | None = None,
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
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
        ...
