"""
DRF Serializers for weather data models.
"""

from rest_framework import serializers

from .models import Station


class StationSerializer(serializers.ModelSerializer):
    code = serializers.CharField(source="station_code", read_only=True)
    nom = serializers.CharField(source="name", read_only=True)
    poste_ouvert = serializers.BooleanField(source="is_open", read_only=True)
    type_poste = serializers.IntegerField(source="station_type", read_only=True)
    poste_public = serializers.BooleanField(source="is_public", read_only=True)

    class Meta:
        model = Station
        fields = [
            "code",
            "nom",
            "departement",
            "poste_ouvert",
            "type_poste",
            "lon",
            "lat",
            "alt",
            "poste_public",
        ]


class StationDetailSerializer(StationSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta(StationSerializer.Meta):
        fields = [*StationSerializer.Meta.fields, "created_at", "updated_at"]


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


class CommaSeparatedStationIdsField(serializers.Field):
    def to_internal_value(self, data):
        if data is None:
            return ()
        if isinstance(data, list | tuple):
            items = [str(x).strip() for x in data if str(x).strip()]
            return tuple(items)

        if isinstance(data, str):
            s = data.strip()
            if not s:
                return ()
            items = [x.strip() for x in s.split(",") if x.strip()]
            return tuple(items)

        raise serializers.ValidationError(
            "Format station_ids invalide. Attendu : liste séparée par des virgules (ex: '07149,07255')."
        )


class TemperatureDeviationQuerySerializer(serializers.Serializer):
    date_start = serializers.DateField(required=True)
    date_end = serializers.DateField(required=True)
    granularity = serializers.ChoiceField(
        choices=["year", "month", "day"], required=True
    )
    station_ids = CommaSeparatedStationIdsField(required=False)
    include_national = serializers.BooleanField(required=False, default=True)

    def validate(self, attrs):
        ds = attrs["date_start"]
        de = attrs["date_end"]
        if ds > de:
            raise serializers.ValidationError(
                {"date_end": "date_end doit être >= date_start."}
            )

        station_ids = attrs.get("station_ids", ())
        include_national = attrs.get("include_national", True)

        if not include_national and len(station_ids) == 0:
            raise serializers.ValidationError(
                {"station_ids": "Requis si include_national=false."}
            )

        attrs["station_ids"] = station_ids
        return attrs


class TemperatureDeviationPointSerializer(serializers.Serializer):
    date = serializers.DateField()
    deviation = serializers.FloatField()
    temperature = serializers.FloatField()
    baseline_mean = serializers.FloatField()


class TemperatureDeviationNationalSerializer(serializers.Serializer):
    data = TemperatureDeviationPointSerializer(many=True)


class TemperatureDeviationStationSerializer(serializers.Serializer):
    station_id = serializers.CharField()
    station_name = serializers.CharField()
    data = TemperatureDeviationPointSerializer(many=True)


class TemperatureDeviationMetadataSerializer(serializers.Serializer):
    date_start = serializers.DateField()
    date_end = serializers.DateField()
    baseline = serializers.CharField()
    granularity = serializers.ChoiceField(choices=["year", "month", "day"])


class TemperatureDeviationResponseSerializer(serializers.Serializer):
    metadata = TemperatureDeviationMetadataSerializer()
    national = TemperatureDeviationNationalSerializer(required=False)
    stations = TemperatureDeviationStationSerializer(many=True)
