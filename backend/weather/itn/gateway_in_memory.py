from collections.abc import Iterable

import pandas as pd


def read_temperatures_using_in_memory_panda(
    stations_itn: Iterable | None = None,
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

    # Ensure stations_itn default is set to an empty tuple to avoid mutable defaults
    if stations_itn is None:
        stations_itn = ()

    # Create a small deterministic set of stations (ids are strings to match
    # how calculate_return_itn checks membership against REIMS_* constants)
    stations_data = [
        {"id": "51449002", "code": "51449002", "nom": "Reims-Prunay"},
        {"id": "51183001", "code": "51183001", "nom": "Reims-Courcy"},
        {"id": "75114001", "code": "75114001", "nom": "Paris - Montsouris"},
        {"id": "13054001", "code": "13054001", "nom": "Marseille - Marignane"},
    ]

    stations = pd.DataFrame(stations_data)

    # If a filter of station codes was provided, keep only matching stations
    if stations_itn and len(stations_itn) > 0:
        # Ensure we compare using the same types (stations_itn may be tuple/list)
        codes_to_keep = set(stations_itn)
        stations = stations[stations["code"].isin(codes_to_keep)].reset_index(drop=True)

    # Build deterministic daily temperatures covering the Reims transition
    # dates so callers that apply the Reims correction can be exercised.
    dates = pd.date_range(start="2012-05-06", end="2012-05-09", freq="D")

    temp_rows = []
    for _, station_row in stations.iterrows():
        station_id = station_row["id"]
        station_nom = station_row["nom"]
        # Use simple but distinct values per station for clarity
        base_min = 5.0
        base_max = 15.0
        if "Reims" in station_nom:
            base_min = 3.0
            base_max = 13.0
        elif "Paris" in station_nom:
            base_min = 6.0
            base_max = 16.0
        elif "Marseille" in station_nom:
            base_min = 10.0
            base_max = 20.0

        for i, d in enumerate(dates):
            # Slightly vary temperatures by date index to avoid identical rows
            tn = base_min + float(i)  # temp_min
            tx = base_max + float(i)  # temp_max
            # tntxm: use a simple mid-point variant that could represent an aggregated value
            tntxm = (tn + tx) / 2.0

            temp_rows.append(
                {
                    "station_id": station_id,
                    "nom": station_nom,
                    "date": d,
                    "temp_max": tx,
                    "temp_min": tn,
                    "tntxm": tntxm,
                }
            )

    temp_daily = pd.DataFrame(temp_rows)

    # Ensure date column is datetime and types are suitable for pivoting
    temp_daily["date"] = pd.to_datetime(temp_daily["date"])

    return stations, temp_daily
