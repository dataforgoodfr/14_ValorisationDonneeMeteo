"""
DRF Serializers for weather data models.
"""

from rest_framework import serializers

from .models import HoraireTempsReel, Quotidienne, Station


class StationSerializer(serializers.ModelSerializer):
    """Serializer for weather station metadata."""

    class Meta:
        model = Station
        fields = [
            "id",
            "code",
            "nom",
            "departement",
            "frequence",
            "poste_ouvert",
            "type_poste",
            "lon",
            "lat",
            "alt",
            "poste_public",
        ]


class StationDetailSerializer(StationSerializer):
    """Detailed serializer including timestamps."""

    class Meta(StationSerializer.Meta):
        fields = [*StationSerializer.Meta.fields, "created_at", "updated_at"]


class HoraireTempsReelSerializer(serializers.ModelSerializer):
    """Serializer for hourly real-time measurements."""

    station_code = serializers.CharField(source="station.code", read_only=True)

    class Meta:
        model = HoraireTempsReel
        fields = [
            "id",
            "station",
            "station_code",
            "lat",
            "lon",
            "validity_time",
            "t",
            "td",
            "tx",
            "tn",
            "u",
            "dd",
            "ff",
            "rr1",
            "vv",
            "n",
            "pres",
            "pmer",
        ]


class HoraireTempsReelDetailSerializer(HoraireTempsReelSerializer):
    """Detailed serializer with all measurement fields."""

    class Meta(HoraireTempsReelSerializer.Meta):
        fields = "__all__"


class QuotidienneSerializer(serializers.ModelSerializer):
    """Serializer for daily aggregated data."""

    station_code = serializers.CharField(source="station.code", read_only=True)

    class Meta:
        model = Quotidienne
        fields = [
            "id",
            "station",
            "station_code",
            "nom_usuel",
            "lat",
            "lon",
            "alti",
            "date",
            "rr",
            "tn",
            "tx",
            "tm",
            "ffm",
            "fxy",
        ]


class QuotidienneDetailSerializer(QuotidienneSerializer):
    """Detailed serializer with all daily fields."""

    class Meta(QuotidienneSerializer.Meta):
        fields = "__all__"


class ErrorSerializer(serializers.Serializer):
    error = serializers.DictField()

    @staticmethod
    def build(code: str, message: str, details: dict | None = None) -> dict:
        payload = {"error": {"code": code, "message": message}}
        if details is not None:
            payload["error"]["details"] = details
        return payload


class NationalIndicatorQuerySerializer(serializers.Serializer):
    date_start = serializers.DateField(required=True)
    date_end = serializers.DateField(required=True)
    aggregation = serializers.ChoiceField(
        choices=["year", "month", "day_of_month"], required=True
    )
    day_of_month = serializers.IntegerField(required=False, min_value=1, max_value=31)

    def validate(self, attrs):
        ds = attrs["date_start"]
        de = attrs["date_end"]
        if ds > de:
            raise serializers.ValidationError(
                {"date_end": "date_end doit être >= date_start."}
            )

        agg = attrs["aggregation"]
        dom = attrs.get("day_of_month")

        if agg == "day_of_month" and dom is None:
            raise serializers.ValidationError(
                {"day_of_month": "Obligatoire si aggregation=day_of_month."}
            )
        if agg != "day_of_month" and dom is not None:
            raise serializers.ValidationError(
                {"day_of_month": "Interdit sauf si aggregation=day_of_month."}
            )
        return attrs


class NationalIndicatorMetadataSerializer(serializers.Serializer):
    date_start = serializers.DateField()
    date_end = serializers.DateField()
    aggregation = serializers.ChoiceField(choices=["year", "month", "day_of_month"])
    day_of_month = serializers.IntegerField(required=False, min_value=1, max_value=31)
    baseline = serializers.CharField()


class NationalIndicatorBaselineStatisticsSerializer(serializers.Serializer):
    mean_temperature = serializers.FloatField()


class NationalIndicatorTimePointSerializer(serializers.Serializer):
    date = serializers.DateField()
    temperature = serializers.FloatField()
    baseline_mean = serializers.FloatField()
    baseline_std_dev_upper = serializers.FloatField()
    baseline_std_dev_lower = serializers.FloatField()
    baseline_max = serializers.FloatField()
    baseline_min = serializers.FloatField()


class NationalIndicatorResponseSerializer(serializers.Serializer):
    metadata = NationalIndicatorMetadataSerializer()
    baseline_statistics = NationalIndicatorBaselineStatisticsSerializer()
    time_series = NationalIndicatorTimePointSerializer(many=True)
