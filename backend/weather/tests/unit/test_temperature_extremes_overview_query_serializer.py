import datetime as dt

from weather.serializers import TemperatureExtremesOverviewQuerySerializer


def _valid(**overrides):
    params = {"date_start": "2024-01-01", "date_end": "2024-12-31"}
    params.update(overrides)
    return TemperatureExtremesOverviewQuerySerializer(data=params)


def test_happy_path_minimal():
    s = _valid()

    assert s.is_valid(), s.errors
    assert s.validated_data["date_start"] == dt.date(2024, 1, 1)
    assert s.validated_data["date_end"] == dt.date(2024, 12, 31)
    assert s.validated_data["type"] == "tx"
    assert s.validated_data["ordering"] == "-txm"
    assert s.validated_data["limit"] == 50
    assert s.validated_data["offset"] == 0
    assert s.validated_data["station_ids"] == ()
    assert s.validated_data["departments"] == ()
    assert s.validated_data["regions"] == ()
    assert s.validated_data["station_search"] is None


def test_type_tn_accepted():
    s = _valid(type="tn")

    assert s.is_valid(), s.errors
    assert s.validated_data["type"] == "tn"


def test_type_invalid_rejected():
    s = _valid(type="tmean")

    assert not s.is_valid()
    assert "type" in s.errors


def test_rejects_date_end_before_date_start():
    s = _valid(date_start="2024-12-31", date_end="2024-01-01")

    assert not s.is_valid()
    assert "date_end" in s.errors


def test_same_date_start_and_date_end_is_valid():
    s = _valid(date_start="2024-06-15", date_end="2024-06-15")

    assert s.is_valid(), s.errors


def test_rejects_missing_date_start():
    s = TemperatureExtremesOverviewQuerySerializer(data={"date_end": "2024-12-31"})

    assert not s.is_valid()
    assert "date_start" in s.errors


def test_rejects_missing_date_end():
    s = TemperatureExtremesOverviewQuerySerializer(data={"date_start": "2024-01-01"})

    assert not s.is_valid()
    assert "date_end" in s.errors


def test_rejects_txn_greater_than_max():
    s = _valid(txn=30, txx=20)

    assert not s.is_valid()
    assert "txx" in s.errors


def test_rejects_tnn_greater_than_max():
    s = _valid(tnn=30, tnx=20)

    assert not s.is_valid()
    assert "tnx" in s.errors


def test_rejects_tmn_greater_than_max():
    s = _valid(tmn=25, tmx=10)

    assert not s.is_valid()
    assert "tmx" in s.errors


def test_rejects_alt_min_greater_than_max():
    s = _valid(alt_min=1000, alt_max=500)

    assert not s.is_valid()
    assert "alt_max" in s.errors


def test_rejects_negative_offset():
    s = _valid(offset=-1)

    assert not s.is_valid()
    assert "offset" in s.errors


def test_rejects_limit_zero():
    s = _valid(limit=0)

    assert not s.is_valid()
    assert "limit" in s.errors


def test_station_ids_parsed_from_comma_separated():
    s = _valid(station_ids="07149,07222,07460")

    assert s.is_valid(), s.errors
    assert s.validated_data["station_ids"] == ("07149", "07222", "07460")


def test_empty_station_ids_normalized_to_empty_tuple():
    s = _valid(station_ids="")

    assert s.is_valid(), s.errors
    assert s.validated_data["station_ids"] == ()


def test_departments_parsed_from_comma_separated():
    s = _valid(departments="13,69,75")

    assert s.is_valid(), s.errors
    assert s.validated_data["departments"] == ("13", "69", "75")


def test_regions_parsed_from_comma_separated():
    s = _valid(regions="Bretagne,Occitanie")

    assert s.is_valid(), s.errors
    assert s.validated_data["regions"] == ("Bretagne", "Occitanie")


def test_station_search_whitespace_stripped():
    s = _valid(station_search="  lyon  ")

    assert s.is_valid(), s.errors
    assert s.validated_data["station_search"] == "lyon"


def test_station_search_blank_normalized_to_none():
    s = _valid(station_search="   ")

    assert s.is_valid(), s.errors
    assert s.validated_data["station_search"] is None


def test_ordering_choices_accepted():
    valid_orderings = [
        "station_name",
        "-station_name",
        "txm",
        "-txm",
        "tnm",
        "-tnm",
        "tmm",
        "-tmm",
        "department",
        "-department",
        "region",
        "-region",
        "alt",
        "-alt",
    ]

    for ordering in valid_orderings:
        s = _valid(ordering=ordering)
        assert s.is_valid(), f"ordering={ordering!r} devrait être valide: {s.errors}"


def test_ordering_invalid_rejected():
    s = _valid(ordering="invalid_field")

    assert not s.is_valid()
    assert "ordering" in s.errors


def test_all_optional_filters_accepted():
    s = _valid(
        type="tn",
        station_ids="07149",
        station_search="lyon",
        tmn=10.0,
        tmx=20.0,
        txn=15.0,
        txx=30.0,
        tnn=5.0,
        tnx=20.0,
        alt_min=100.0,
        alt_max=500.0,
        departments="69",
        regions="Auvergne-Rhône-Alpes",
        ordering="station_name",
        limit=25,
        offset=50,
    )

    assert s.is_valid(), s.errors
    d = s.validated_data
    assert d["type"] == "tn"
    assert d["tmn"] == 10.0
    assert d["tmx"] == 20.0
    assert d["txn"] == 15.0
    assert d["txx"] == 30.0
    assert d["tnn"] == 5.0
    assert d["tnx"] == 20.0
    assert d["alt_min"] == 100.0
    assert d["alt_max"] == 500.0
    assert d["limit"] == 25
    assert d["offset"] == 50


def test_parses_classe_recente():
    s = _valid(classe_recente_min=1, classe_recente_max=3)
    assert s.is_valid(), s.errors
    assert s.validated_data["classe_recente_min"] == 1
    assert s.validated_data["classe_recente_max"] == 3


def test_rejects_classe_recente_inverted_bounds():
    s = _valid(classe_recente_min=3, classe_recente_max=1)
    assert not s.is_valid()
    assert "classe_recente_max" in s.errors


def test_parses_date_de_creation():
    s = _valid(date_de_creation_min="1900-01-01", date_de_creation_max="1960-12-31")
    assert s.is_valid(), s.errors
    assert s.validated_data["date_de_creation_min"] == dt.date(1900, 1, 1)
    assert s.validated_data["date_de_creation_max"] == dt.date(1960, 12, 31)


def test_rejects_date_de_creation_inverted_bounds():
    s = _valid(date_de_creation_min="1960-01-01", date_de_creation_max="1900-01-01")
    assert not s.is_valid()
    assert "date_de_creation_max" in s.errors


def test_parses_date_de_fermeture():
    s = _valid(date_de_fermeture_min="2000-01-01", date_de_fermeture_max="2020-12-31")
    assert s.is_valid(), s.errors
    assert s.validated_data["date_de_fermeture_min"] == dt.date(2000, 1, 1)
    assert s.validated_data["date_de_fermeture_max"] == dt.date(2020, 12, 31)


def test_rejects_date_de_fermeture_inverted_bounds():
    s = _valid(date_de_fermeture_min="2020-01-01", date_de_fermeture_max="2000-01-01")
    assert not s.is_valid()
    assert "date_de_fermeture_max" in s.errors


def test_defaults_lifecycle_fields_to_none():
    s = _valid()
    assert s.is_valid(), s.errors
    assert s.validated_data["classe_recente_min"] is None
    assert s.validated_data["classe_recente_max"] is None
    assert s.validated_data["date_de_creation_min"] is None
    assert s.validated_data["date_de_creation_max"] is None
    assert s.validated_data["date_de_fermeture_min"] is None
    assert s.validated_data["date_de_fermeture_max"] is None
