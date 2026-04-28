import datetime as dt

from weather.serializers import TemperatureRecordsQuerySerializer


def test_records_query_serializer_defaults_to_all_time_hot():
    s = TemperatureRecordsQuerySerializer(data={})
    assert s.is_valid(), s.errors
    assert s.validated_data["period_type"] == "all_time"
    assert s.validated_data["type_records"] == "hot"


def test_records_query_serializer_month_happy_path():
    s = TemperatureRecordsQuerySerializer(
        data={"period_type": "month", "month": 7, "type_records": "hot"}
    )
    assert s.is_valid(), s.errors
    assert s.validated_data["month"] == 7


def test_records_query_serializer_season_happy_path():
    s = TemperatureRecordsQuerySerializer(
        data={"period_type": "season", "season": "winter", "type_records": "cold"}
    )
    assert s.is_valid(), s.errors
    assert s.validated_data["season"] == "winter"
    assert s.validated_data["type_records"] == "cold"


def test_records_query_serializer_all_time_happy_path():
    s = TemperatureRecordsQuerySerializer(
        data={"period_type": "all_time", "type_records": "hot"}
    )
    assert s.is_valid(), s.errors


def test_records_query_serializer_rejects_month_missing_when_period_type_month():
    s = TemperatureRecordsQuerySerializer(
        data={"period_type": "month", "type_records": "hot"}
    )
    assert not s.is_valid()
    assert "month" in s.errors


def test_records_query_serializer_rejects_season_missing_when_period_type_season():
    s = TemperatureRecordsQuerySerializer(
        data={"period_type": "season", "type_records": "cold"}
    )
    assert not s.is_valid()
    assert "season" in s.errors


def test_records_query_serializer_rejects_unknown_period_type():
    s = TemperatureRecordsQuerySerializer(
        data={"period_type": "weekly", "type_records": "hot"}
    )
    assert not s.is_valid()
    assert "period_type" in s.errors


def test_records_query_serializer_rejects_month_out_of_range():
    s = TemperatureRecordsQuerySerializer(
        data={"period_type": "month", "month": 13, "type_records": "hot"}
    )
    assert not s.is_valid()
    assert "month" in s.errors


def test_records_query_serializer_rejects_unknown_season():
    s = TemperatureRecordsQuerySerializer(
        data={"period_type": "season", "season": "monsoon", "type_records": "cold"}
    )
    assert not s.is_valid()
    assert "season" in s.errors


def test_records_query_serializer_sort_single_field():
    s = TemperatureRecordsQuerySerializer(data={"sort": "station_name"})
    assert s.is_valid(), s.errors
    assert s.validated_data["sort"] == "station_name"


def test_records_query_serializer_sort_multiple_fields():
    # Test avec plusieurs champs et un tri descendant (-)
    s = TemperatureRecordsQuerySerializer(data={"sort": "station_name,-record_value"})
    assert s.is_valid(), s.errors
    assert s.validated_data["sort"] == "station_name,-record_value"


def test_records_query_serializer_rejects_invalid_sort_field():
    # Test avec un champ qui n'existe pas (ex: 'population')
    s = TemperatureRecordsQuerySerializer(data={"sort": "population"})
    assert not s.is_valid()
    assert "sort" in s.errors
    # Vérifie que le message d'erreur mentionne le champ invalide
    assert "Champ de tri 'population' invalide" in str(s.errors["sort"][0])


# --- Tests pour la Pagination ---


def test_records_query_serializer_pagination_valid():
    s = TemperatureRecordsQuerySerializer(data={"page": 2, "page_size": 50})
    assert s.is_valid(), s.errors
    assert s.validated_data["page"] == 2
    assert s.validated_data["page_size"] == 50


def test_records_query_serializer_pagination_defaults():
    s = TemperatureRecordsQuerySerializer(data={})
    assert s.is_valid()
    # Vérifie si ton serializer a des valeurs par défaut (ex: page 1)
    # Adapte les valeurs ci-dessous selon ton code
    assert s.validated_data.get("page", 1) == 1


def test_records_query_serializer_rejects_negative_page():
    s = TemperatureRecordsQuerySerializer(data={"page": -1})
    assert not s.is_valid()
    assert "page" in s.errors


def test_records_query_serializer_rejects_invalid_page_size():
    # Test si le page_size est trop grand ou n'est pas un nombre
    s = TemperatureRecordsQuerySerializer(data={"page_size": "beaucoup"})
    assert not s.is_valid()
    assert "page_size" in s.errors


# ---------------------------------------------------------------------------
# Filtres classe_recente / date_de_creation / date_de_fermeture
# ---------------------------------------------------------------------------


def test_records_query_serializer_accepts_classe_recente_min_max():
    s = TemperatureRecordsQuerySerializer(
        data={"classe_recente_min": 1, "classe_recente_max": 3}
    )
    assert s.is_valid(), s.errors
    assert s.validated_data["classe_recente_min"] == 1
    assert s.validated_data["classe_recente_max"] == 3


def test_records_query_serializer_rejects_classe_recente_min_gt_max():
    s = TemperatureRecordsQuerySerializer(
        data={"classe_recente_min": 4, "classe_recente_max": 2}
    )
    assert not s.is_valid()
    assert "classe_recente_max" in s.errors


def test_records_query_serializer_rejects_classe_recente_out_of_bounds():
    s = TemperatureRecordsQuerySerializer(data={"classe_recente_min": 0})
    assert not s.is_valid()
    assert "classe_recente_min" in s.errors

    s2 = TemperatureRecordsQuerySerializer(data={"classe_recente_max": 6})
    assert not s2.is_valid()
    assert "classe_recente_max" in s2.errors


def test_records_query_serializer_accepts_date_de_creation_range():
    s = TemperatureRecordsQuerySerializer(
        data={
            "date_de_creation_min": "1920-01-01",
            "date_de_creation_max": "1980-01-01",
        }
    )
    assert s.is_valid(), s.errors
    assert s.validated_data["date_de_creation_min"] == dt.date(1920, 1, 1)
    assert s.validated_data["date_de_creation_max"] == dt.date(1980, 1, 1)


def test_records_query_serializer_rejects_date_de_creation_min_gt_max():
    s = TemperatureRecordsQuerySerializer(
        data={
            "date_de_creation_min": "1990-01-01",
            "date_de_creation_max": "1950-01-01",
        }
    )
    assert not s.is_valid()
    assert "date_de_creation_max" in s.errors


def test_records_query_serializer_rejects_date_de_fermeture_min_gt_max():
    s = TemperatureRecordsQuerySerializer(
        data={
            "date_de_fermeture_min": "2010-01-01",
            "date_de_fermeture_max": "2005-01-01",
        }
    )
    assert not s.is_valid()
    assert "date_de_fermeture_max" in s.errors


def test_records_query_serializer_normalizes_absent_filters_to_none():
    """Champs absents → normalisés à None par validate()."""
    s = TemperatureRecordsQuerySerializer(data={})
    assert s.is_valid(), s.errors
    assert s.validated_data["classe_recente_min"] is None
    assert s.validated_data["classe_recente_max"] is None
    assert s.validated_data["date_de_creation_min"] is None
    assert s.validated_data["date_de_creation_max"] is None
    assert s.validated_data["date_de_fermeture_min"] is None
    assert s.validated_data["date_de_fermeture_max"] is None
