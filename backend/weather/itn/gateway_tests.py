import datetime
from collections.abc import Iterable

import numpy as np
import pandas as pd

from weather.calcul_itn import (
    DEFAULT_ITN_STATIONS_LIST,
    REIMS_COURCY_ID,
    REIMS_PRUNAY_ID,
)


class ReadTemperaturesTests:
    def read_temperatures(
        self,
        stations_itn: Iterable | None = None,
        start_date: str | pd.Timestamp | datetime.datetime | None = None,
        end_date: str | pd.Timestamp | datetime.datetime | None = None,
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Read a fixed in-memory dataset and return two pandas DataFrames that
        mimic the result of `read_temperatures_using_database`.

        The returned `stations` DataFrame contains columns: id, code, nom
        The returned `temp_daily` DataFrame contains columns:
            station_id, nom, date, temp_max, temp_min, tntxm

        The function accepts an optional `stations_itn` iterable of station codes
        and will filter the returned stations (by `code`) and the temperature
        records accordingly. This keeps behaviour compatible with the DB gateway.
        """

        # Ensure stations_itn default is set to the default tuple
        if stations_itn is None:
            stations_itn = DEFAULT_ITN_STATIONS_LIST

        dates = pd.to_datetime(["2012-05-06", "2012-05-07", "2012-05-08", "2012-05-09"])

        # Create a small deterministic set of stations
        stations = pd.DataFrame(
            [
                {"id": REIMS_COURCY_ID, "code": REIMS_COURCY_ID, "nom": "Reims-Courcy"},
                {"id": REIMS_PRUNAY_ID, "code": REIMS_PRUNAY_ID, "nom": "Reims-Prunay"},
                {"id": "75114001", "code": "75114001", "nom": "Paris - Montsouris"},
                {"id": "13054001", "code": "13054001", "nom": "Marseille - Marignane"},
            ]
        )

        # Keep only stations matching the filter of station codes
        codes_to_keep = set(stations_itn)
        stations = stations[stations["code"].isin(codes_to_keep)].reset_index(drop=True)

        # Build deterministic daily temperatures covering the Reims transition dates
        temp_daily = pd.DataFrame(
            [
                {
                    "station_id": REIMS_COURCY_ID,
                    "nom": "Reims-Courcy",
                    "date": dates[0],
                    "temp_max": 13.0,
                    "temp_min": 3.0,
                    "tntxm": 8.0,
                },
                {
                    "station_id": REIMS_COURCY_ID,
                    "nom": "Reims-Courcy",
                    "date": dates[1],
                    "temp_max": 14.0,
                    "temp_min": 4.0,
                    "tntxm": 9.0,
                },
                {
                    "station_id": REIMS_COURCY_ID,
                    "nom": "Reims-Courcy",
                    "date": dates[2],
                    "temp_max": 15.0,
                    "temp_min": 5.0,
                    "tntxm": 10.0,
                },
                {
                    "station_id": REIMS_COURCY_ID,
                    "nom": "Reims-Courcy",
                    "date": dates[3],
                    "temp_max": 16.0,
                    "temp_min": 6.0,
                    "tntxm": 11.0,
                },
                {
                    "station_id": REIMS_PRUNAY_ID,
                    "nom": "Reims-Prunay",
                    "date": dates[0],
                    "temp_max": 14.0,
                    "temp_min": 4.0,
                    "tntxm": 9.0,
                },
                {
                    "station_id": REIMS_PRUNAY_ID,
                    "nom": "Reims-Prunay",
                    "date": dates[1],
                    "temp_max": 15.0,
                    "temp_min": 5.0,
                    "tntxm": 10.0,
                },
                {
                    "station_id": REIMS_PRUNAY_ID,
                    "nom": "Reims-Prunay",
                    "date": dates[2],
                    "temp_max": 16.0,
                    "temp_min": 6.0,
                    "tntxm": 11.0,
                },
                {
                    "station_id": REIMS_PRUNAY_ID,
                    "nom": "Reims-Prunay",
                    "date": dates[3],
                    "temp_max": 17.0,
                    "temp_min": 7.0,
                    "tntxm": 12.0,
                },
                {
                    "station_id": "75114001",
                    "nom": "Paris - Montsouris",
                    "date": dates[0],
                    "temp_max": 8.0,
                    "temp_min": -2.0,
                    "tntxm": 3.0,
                },
                {
                    "station_id": "75114001",
                    "nom": "Paris - Montsouris",
                    "date": dates[1],
                    "temp_max": 9.0,
                    "temp_min": -1.0,
                    "tntxm": 4.0,
                },
                {
                    "station_id": "75114001",
                    "nom": "Paris - Montsouris",
                    "date": dates[2],
                    "temp_max": 10.0,
                    "temp_min": 0.0,
                    "tntxm": 5.0,
                },
                {
                    "station_id": "75114001",
                    "nom": "Paris - Montsouris",
                    "date": dates[3],
                    "temp_max": 11.0,
                    "temp_min": 1.0,
                    "tntxm": 6.0,
                },
                {
                    "station_id": "13054001",
                    "nom": "Marseille - Marignane",
                    "date": dates[0],
                    "temp_max": 20.0,
                    "temp_min": 10.0,
                    "tntxm": 15.0,
                },
                {
                    "station_id": "13054001",
                    "nom": "Marseille - Marignane",
                    "date": dates[1],
                    "temp_max": 21.0,
                    "temp_min": 11.0,
                    "tntxm": 16.0,
                },
                {
                    "station_id": "13054001",
                    "nom": "Marseille - Marignane",
                    "date": dates[2],
                    "temp_max": 22.0,
                    "temp_min": 12.0,
                    "tntxm": 17.0,
                },
                {
                    "station_id": "13054001",
                    "nom": "Marseille - Marignane",
                    "date": dates[3],
                    "temp_max": 23.0,
                    "temp_min": 13.0,
                    "tntxm": 18.0,
                },
            ]
        )

        # Ensure date column is datetime
        temp_daily["date"] = pd.to_datetime(temp_daily["date"])

        return stations, temp_daily


class ReadMonthlyTemperaturesTests:
    def read_temperatures(
        self,
        stations_itn: Iterable | None = None,
        start_date: str | pd.Timestamp | datetime.datetime | None = None,
        end_date: str | pd.Timestamp | datetime.datetime | None = None,
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Read a fixed in-memory dataset and return two pandas DataFrames that
        mimic the result of `read_temperatures_using_database`.end_date

        The returned `stations` DataFrame contains columns: id, code, nom
        The returned `temp_daily` DataFrame contains columns:
            station_id, nom, date, temp_max, temp_min, tntxm

        The function accepts an optional `stations_itn` iterable of station codes
        and will filter the returned stations (by `code`) and the temperature
        records accordingly. This keeps behaviour compatible with the DB gateway.
        """

        # Ensure stations_itn default is set to the default tuple
        if stations_itn is None:
            stations_itn = DEFAULT_ITN_STATIONS_LIST

        dates = pd.date_range("2024-01-01", "2024-03-31", freq="D")
        time_steps = np.concatenate(
            (
                np.linspace(0, 2 * np.pi, 31),
                np.linspace(0, 6 * np.pi, 29),
                np.linspace(0, 4 * np.pi, 31),
            )
        )

        # Create a small deterministic set of stations
        stations = pd.DataFrame(
            [
                {"id": REIMS_COURCY_ID, "code": REIMS_COURCY_ID, "nom": "Reims-Courcy"},
                {"id": REIMS_PRUNAY_ID, "code": REIMS_PRUNAY_ID, "nom": "Reims-Prunay"},
                {"id": "75114001", "code": "75114001", "nom": "Paris - Montsouris"},
                {"id": "13054001", "code": "13054001", "nom": "Marseille - Marignane"},
            ]
        )

        # Keep only stations matching the filter of station codes
        codes_to_keep = set(stations_itn)
        stations = stations[stations["code"].isin(codes_to_keep)].reset_index(drop=True)

        # Build deterministic daily temperatures covering the Reims transition dates
        temp_daily = pd.DataFrame(
            {
                "station_id": [REIMS_COURCY_ID for date in dates]
                + [REIMS_PRUNAY_ID for date in dates]
                + ["75114001" for date in dates]
                + ["13054001" for date in dates],
                "nom": ["Reims-Courcy" for date in dates]
                + ["Reims-Prunay" for date in dates]
                + ["Paris - Montsouris" for date in dates]
                + ["Marseille - Marignane" for date in dates],
                "date": dates.to_list()
                + dates.to_list()
                + dates.to_list()
                + dates.to_list(),
                "temp_max": list(15 + np.sin(time_steps))
                + list(16 + np.sin(time_steps))
                + list(8 + np.sin(time_steps))
                + list(22 + np.sin(time_steps)),
                "temp_min": list(5 + np.sin(time_steps))
                + list(6 + np.sin(time_steps))
                + list(-2 + np.sin(time_steps))
                + list(12 + np.sin(time_steps)),
                "tntxm": list(10 + np.sin(time_steps))
                + list(11 + np.sin(time_steps))
                + list(3 + np.sin(time_steps))
                + list(17 + np.sin(time_steps)),
            }
        )

        # Ensure date column is datetime
        temp_daily["date"] = pd.to_datetime(temp_daily["date"])

        return stations, temp_daily


class ReadYearlyTemperaturesTests:
    def read_temperatures(
        self,
        stations_itn: Iterable | None = None,
        start_date: str | pd.Timestamp | datetime.datetime | None = None,
        end_date: str | pd.Timestamp | datetime.datetime | None = None,
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Read a fixed in-memory dataset and return two pandas DataFrames that
        mimic the result of `read_temperatures_using_database`.end_date

        The returned `stations` DataFrame contains columns: id, code, nom
        The returned `temp_daily` DataFrame contains columns:
            station_id, nom, date, temp_max, temp_min, tntxm

        The function accepts an optional `stations_itn` iterable of station codes
        and will filter the returned stations (by `code`) and the temperature
        records accordingly. This keeps behaviour compatible with the DB gateway.
        """

        # Ensure stations_itn default is set to the default tuple
        if stations_itn is None:
            stations_itn = DEFAULT_ITN_STATIONS_LIST

        dates = pd.date_range("2021-01-01", "2023-12-31", freq="D")
        time_steps = np.concatenate(
            (
                np.linspace(0, 2 * np.pi, 365),
                np.linspace(0, 6 * np.pi, 365),
                np.linspace(0, 4 * np.pi, 365),
            )
        )

        # Create a small deterministic set of stations
        stations = pd.DataFrame(
            [
                {"id": REIMS_COURCY_ID, "code": REIMS_COURCY_ID, "nom": "Reims-Courcy"},
                {"id": REIMS_PRUNAY_ID, "code": REIMS_PRUNAY_ID, "nom": "Reims-Prunay"},
                {"id": "75114001", "code": "75114001", "nom": "Paris - Montsouris"},
                {"id": "13054001", "code": "13054001", "nom": "Marseille - Marignane"},
            ]
        )

        # Keep only stations matching the filter of station codes
        codes_to_keep = set(stations_itn)
        stations = stations[stations["code"].isin(codes_to_keep)].reset_index(drop=True)

        # Build deterministic daily temperatures covering the Reims transition dates
        temp_daily = pd.DataFrame(
            {
                "station_id": [REIMS_COURCY_ID for date in dates]
                + [REIMS_PRUNAY_ID for date in dates]
                + ["75114001" for date in dates]
                + ["13054001" for date in dates],
                "nom": ["Reims-Courcy" for date in dates]
                + ["Reims-Prunay" for date in dates]
                + ["Paris - Montsouris" for date in dates]
                + ["Marseille - Marignane" for date in dates],
                "date": dates.to_list()
                + dates.to_list()
                + dates.to_list()
                + dates.to_list(),
                "temp_max": list(17 + np.sin(time_steps))
                + list(19 + np.sin(time_steps))
                + list(6 + np.sin(time_steps))
                + list(26 + np.sin(time_steps)),
                "temp_min": list(7 + np.sin(time_steps))
                + list(9 + np.sin(time_steps))
                + list(-8 + np.sin(time_steps))
                + list(16 + np.sin(time_steps)),
                "tntxm": list(12 + np.sin(time_steps))
                + list(14 + np.sin(time_steps))
                + list(-1 + np.sin(time_steps))
                + list(21 + np.sin(time_steps)),
            }
        )

        # Ensure date column is datetime
        temp_daily["date"] = pd.to_datetime(temp_daily["date"])

        return stations, temp_daily
