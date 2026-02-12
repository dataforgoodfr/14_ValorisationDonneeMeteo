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

    granularity = serializers.ChoiceField(
        choices=["year", "month", "day"], required=True
    )

    slice_type = serializers.ChoiceField(
        choices=["full", "month_of_year", "day_of_month"],
        required=False,
        default="full",
    )

    month_of_year = serializers.IntegerField(required=False, min_value=1, max_value=12)
    day_of_month = serializers.IntegerField(required=False, min_value=1, max_value=31)

    def validate(self, attrs):
        ds = attrs["date_start"]
        de = attrs["date_end"]
        if ds > de:
            raise serializers.ValidationError(
                {"date_end": "date_end doit être >= date_start."}
            )

        gran = attrs["granularity"]
        slice_type = attrs.get("slice_type", "full")
        moy = attrs.get("month_of_year")
        dom = attrs.get("day_of_month")

        # granularity=day => slice_type doit être full + pas de month/day selectors
        if gran == "day":
            if slice_type != "full":
                raise serializers.ValidationError(
                    {"slice_type": "Interdit si granularity=day (doit être full)."}
                )
            if moy is not None:
                raise serializers.ValidationError(
                    {"month_of_year": "Interdit si granularity=day."}
                )
            if dom is not None:
                raise serializers.ValidationError(
                    {"day_of_month": "Interdit si granularity=day."}
                )
            return attrs

        if slice_type == "full":
            if moy is not None:
                raise serializers.ValidationError(
                    {"month_of_year": "Interdit si slice_type=full."}
                )
            if dom is not None:
                raise serializers.ValidationError(
                    {"day_of_month": "Interdit si slice_type=full."}
                )
            return attrs

        elif slice_type == "month_of_year":
            # validé par spec: seulement pour granularity=year
            if gran != "year":
                raise serializers.ValidationError(
                    {
                        "slice_type": "month_of_year n'est valide que si granularity=year."
                    }
                )
            if moy is None:
                raise serializers.ValidationError(
                    {"month_of_year": "Requis si slice_type=month_of_year."}
                )
            if dom is not None:
                raise serializers.ValidationError(
                    {"day_of_month": "Interdit si slice_type=month_of_year."}
                )
            return attrs

        # slice_type == "day_of_month"
        if dom is None:
            raise serializers.ValidationError(
                {"day_of_month": "Requis si slice_type=day_of_month."}
            )

        if gran == "year":
            # jour précis de l'année => month_of_year requis
            if moy is None:
                raise serializers.ValidationError(
                    {
                        "month_of_year": "Requis si granularity=year et slice_type=day_of_month."
                    }
                )
        else:
            # granularity=month => month_of_year interdit
            if moy is not None:
                raise serializers.ValidationError(
                    {"month_of_year": "Interdit si granularity=month."}
                )

        return attrs


class NationalIndicatorTimePointSerializer(serializers.Serializer):
    date = serializers.DateField()
    temperature = serializers.FloatField()
    baseline_mean = serializers.FloatField()
    baseline_std_dev_upper = serializers.FloatField()
    baseline_std_dev_lower = serializers.FloatField()
    baseline_max = serializers.FloatField()
    baseline_min = serializers.FloatField()


class NationalIndicatorMetadataSerializer(serializers.Serializer):
    date_start = serializers.DateField()
    date_end = serializers.DateField()
    baseline = serializers.CharField()
    granularity = serializers.ChoiceField(choices=["year", "month", "day"])
    slice_type = serializers.ChoiceField(
        choices=["full", "month_of_year", "day_of_month"]
    )
    month_of_year = serializers.IntegerField(required=False, min_value=1, max_value=12)
    day_of_month = serializers.IntegerField(required=False, min_value=1, max_value=31)


class NationalIndicatorResponseSerializer(serializers.Serializer):
    metadata = NationalIndicatorMetadataSerializer()
    time_series = NationalIndicatorTimePointSerializer(many=True)
