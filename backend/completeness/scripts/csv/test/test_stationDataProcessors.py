import pandas as pd
from stationDataProcessors import *


def test_station_class_data_casting():
    """
    Valide que les colonnes du DataFrame sont correctement typées.
    """
    test_station_csv = StationDataProcessor('test')
    test_raw_df = pd.DataFrame({
        "station_code": [101, 102],
        "classe": ["18", "20"],
        "date_debut": ["2026-05-01", "2026-05-02"],
        "date_fin": ["2026-05-01", "2026-05-02"]
    })
    test_station_csv.df_raw_station_classe = test_raw_df
    result = test_station_csv.prepare_table_station_classe()


    assert result["station_code"].dtype == "str"
    assert result["classe"].dtype == "Int64"
    assert str(result["date_debut"].dtype).startswith("datetime64")
    assert str(result["date_fin"].dtype).startswith("datetime64")


def test_station_creation_date_casting():
    """
    Valide que les colonnes du DataFrame sont correctement typées.
    """
    test_station_csv = StationDataProcessor('test')
    test_raw_df = pd.DataFrame({
        "station_code": [101, 102],
        "creation_date": ["2026-05-01", "2026-05-02"],
        "date_fin": ["2026-05-01", "2026-05-02"]
    })
    test_station_csv.df_raw_station_creation_date= test_raw_df
    result = test_station_csv.prepare_table_station_creation_date()


    assert result["station_code"].dtype == "str"
    assert str(result["date_de_creation"].dtype).startswith("datetime64")
    assert result["annee_de_fermeture"].dtype == "Int64"






