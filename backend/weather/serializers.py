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
    class Meta(StationSerializer.Meta):
        pass


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


class CommaSeparatedStringListField(serializers.Field):
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
            "Format invalide. Attendu : liste séparée par des virgules."
        )


class TemperatureDeviationGraphQuerySerializer(serializers.Serializer):
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

    station_ids = CommaSeparatedStringListField(required=False)
    include_national = serializers.BooleanField(required=False, default=True)

    def _validate_day_granularity_slice_constraints(
        self,
        *,
        slice_type: str,
        month_of_year: int | None,
        day_of_month: int | None,
    ) -> None:
        if slice_type != "full":
            raise serializers.ValidationError(
                {"slice_type": "Interdit si granularity=day (doit être full)."}
            )
        if month_of_year is not None:
            raise serializers.ValidationError(
                {"month_of_year": "Interdit si granularity=day."}
            )
        if day_of_month is not None:
            raise serializers.ValidationError(
                {"day_of_month": "Interdit si granularity=day."}
            )

    def _validate_full_slice_constraints(
        self,
        *,
        month_of_year: int | None,
        day_of_month: int | None,
    ) -> None:
        if month_of_year is not None:
            raise serializers.ValidationError(
                {"month_of_year": "Interdit si slice_type=full."}
            )
        if day_of_month is not None:
            raise serializers.ValidationError(
                {"day_of_month": "Interdit si slice_type=full."}
            )

    def _validate_month_of_year_slice_constraints(
        self,
        *,
        granularity: str,
        month_of_year: int | None,
        day_of_month: int | None,
    ) -> None:
        if granularity != "year":
            raise serializers.ValidationError(
                {"slice_type": "month_of_year n'est valide que si granularity=year."}
            )
        if month_of_year is None:
            raise serializers.ValidationError(
                {"month_of_year": "Requis si slice_type=month_of_year."}
            )
        if day_of_month is not None:
            raise serializers.ValidationError(
                {"day_of_month": "Interdit si slice_type=month_of_year."}
            )

    def _validate_day_of_month_slice_constraints(
        self,
        *,
        granularity: str,
        month_of_year: int | None,
        day_of_month: int | None,
    ) -> None:
        if day_of_month is None:
            raise serializers.ValidationError(
                {"day_of_month": "Requis si slice_type=day_of_month."}
            )

        if granularity == "year":
            if month_of_year is None:
                raise serializers.ValidationError(
                    {
                        "month_of_year": "Requis si granularity=year et slice_type=day_of_month."
                    }
                )
        else:
            # granularity=month
            if month_of_year is not None:
                raise serializers.ValidationError(
                    {"month_of_year": "Interdit si granularity=month."}
                )

    def validate(self, attrs):
        date_start = attrs["date_start"]
        date_end = attrs["date_end"]
        if date_start > date_end:
            raise serializers.ValidationError(
                {"date_end": "date_end doit être >= date_start."}
            )

        granularity = attrs["granularity"]
        slice_type = attrs.get("slice_type", "full")
        month_of_year = attrs.get("month_of_year")
        day_of_month = attrs.get("day_of_month")

        # granularity=day => slice_type doit être full + pas de month/day selectors
        if granularity == "day":
            self._validate_day_granularity_slice_constraints(
                slice_type=slice_type,
                month_of_year=month_of_year,
                day_of_month=day_of_month,
            )

        elif slice_type == "full":
            self._validate_full_slice_constraints(
                month_of_year=month_of_year,
                day_of_month=day_of_month,
            )

        elif slice_type == "month_of_year":
            self._validate_month_of_year_slice_constraints(
                granularity=granularity,
                month_of_year=month_of_year,
                day_of_month=day_of_month,
            )

        else:
            # slice_type == "day_of_month"
            self._validate_day_of_month_slice_constraints(
                granularity=granularity,
                month_of_year=month_of_year,
                day_of_month=day_of_month,
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
    slice_type = serializers.ChoiceField(
        choices=["full", "month_of_year", "day_of_month"]
    )
    month_of_year = serializers.IntegerField(required=False, min_value=1, max_value=12)
    day_of_month = serializers.IntegerField(required=False, min_value=1, max_value=31)


class TemperatureDeviationResponseSerializer(serializers.Serializer):
    metadata = TemperatureDeviationMetadataSerializer()
    national = TemperatureDeviationNationalSerializer(required=False)
    stations = TemperatureDeviationStationSerializer(many=True)


class TemperatureRecordsQuerySerializer(serializers.Serializer):
    period_type = serializers.ChoiceField(
        choices=["month", "season", "all_time"],
        required=False,
        default="all_time",
    )
    month = serializers.IntegerField(required=False, min_value=1, max_value=12)
    season = serializers.ChoiceField(
        choices=["spring", "summer", "autumn", "winter"],
        required=False,
    )
    type_records = serializers.ChoiceField(
        choices=["hot", "cold"],
        required=False,
        default="hot",
    )
    date_start = serializers.DateField(required=False)
    date_end = serializers.DateField(required=False)
    territoire = serializers.ChoiceField(
        choices=["france", "region", "department", "station"],
        required=False,
        default="france",
    )
    territoire_id = serializers.CharField(required=False)

    def validate(self, attrs):
        period_type = attrs.get("period_type", "all_time")
        month = attrs.get("month")
        season = attrs.get("season")
        date_start = attrs.get("date_start")
        date_end = attrs.get("date_end")
        territoire = attrs.get("territoire", "france")
        territoire_id = attrs.get("territoire_id")

        if period_type == "month" and month is None:
            raise serializers.ValidationError({"month": "Requis si period_type=month."})

        if period_type == "season" and season is None:
            raise serializers.ValidationError(
                {"season": "Requis si period_type=season."}
            )

        if (date_start is None) != (date_end is None):
            raise serializers.ValidationError(
                {"date_start": "date_start et date_end doivent être fournis ensemble."}
            )

        if territoire != "france" and not territoire_id:
            raise serializers.ValidationError(
                {"territoire_id": f"Requis si territoire={territoire}."}
            )

        return attrs


class TemperatureRecordEntrySerializer(serializers.Serializer):
    station_id = serializers.CharField()
    station_name = serializers.CharField()
    department = serializers.CharField()
    record_value = serializers.FloatField()
    record_date = serializers.DateField()
    lat = serializers.FloatField()
    lon = serializers.FloatField()
    alt = serializers.FloatField()


class TemperatureDeviationOverviewQuerySerializer(serializers.Serializer):
    date_start = serializers.DateField(required=True)
    date_end = serializers.DateField(required=True)

    station_ids = CommaSeparatedStringListField(required=False)
    station_search = serializers.CharField(required=False, allow_blank=True)

    temperature_mean_min = serializers.FloatField(required=False, allow_null=True)
    temperature_mean_max = serializers.FloatField(required=False, allow_null=True)

    deviation_min = serializers.FloatField(required=False, allow_null=True)
    deviation_max = serializers.FloatField(required=False, allow_null=True)

    alt_min = serializers.FloatField(required=False, allow_null=True)
    alt_max = serializers.FloatField(required=False, allow_null=True)

    departments = CommaSeparatedStringListField(required=False)
    regions = CommaSeparatedStringListField(required=False)

    ordering = serializers.ChoiceField(
        choices=[
            "station_name",
            "-station_name",
            "temperature_mean",
            "-temperature_mean",
            "deviation",
            "-deviation",
            "department",
            "-department",
            "region",
            "-region",
        ],
        required=False,
        default="-deviation",
    )

    limit = serializers.IntegerField(
        required=False,
        min_value=1,
        default=50,
    )
    offset = serializers.IntegerField(required=False, min_value=0, default=0)

    def validate(self, attrs):
        ds = attrs["date_start"]
        de = attrs["date_end"]
        if ds > de:
            raise serializers.ValidationError(
                {"date_end": "date_end doit être >= date_start."}
            )

        tmin = attrs.get("temperature_mean_min")
        tmax = attrs.get("temperature_mean_max")
        if tmin is not None and tmax is not None and tmin > tmax:
            raise serializers.ValidationError(
                {
                    "temperature_mean_max": (
                        "temperature_mean_max doit être >= temperature_mean_min."
                    )
                }
            )

        dmin = attrs.get("deviation_min")
        dmax = attrs.get("deviation_max")
        if dmin is not None and dmax is not None and dmin > dmax:
            raise serializers.ValidationError(
                {"deviation_max": "deviation_max doit être >= deviation_min."}
            )

        alt_min = attrs.get("alt_min")
        alt_max = attrs.get("alt_max")
        if alt_min is not None and alt_max is not None and alt_min > alt_max:
            raise serializers.ValidationError(
                {"alt_max": "alt_max doit être >= alt_min."}
            )

        station_search = attrs.get("station_search")
        if station_search is not None:
            attrs["station_search"] = station_search.strip()

        attrs["temperature_mean_min"] = (
            tmin if "temperature_mean_min" in attrs else None
        )
        attrs["temperature_mean_max"] = (
            tmax if "temperature_mean_max" in attrs else None
        )
        attrs["deviation_min"] = dmin if "deviation_min" in attrs else None
        attrs["deviation_max"] = dmax if "deviation_max" in attrs else None
        attrs["alt_min"] = alt_min if "alt_min" in attrs else None
        attrs["alt_max"] = alt_max if "alt_max" in attrs else None

        attrs["departments"] = attrs.get("departments", ())
        attrs["regions"] = attrs.get("regions", ())
        attrs["station_ids"] = attrs.get("station_ids", ())

        attrs["station_search"] = attrs.get("station_search") or None

        return attrs


class PaginationMetadataSerializer(serializers.Serializer):
    total_count = serializers.IntegerField()
    limit = serializers.IntegerField()
    offset = serializers.IntegerField()


class TemperatureDeviationOverviewNationalSerializer(serializers.Serializer):
    deviation_mean = serializers.FloatField()


class TemperatureDeviationOverviewStationSerializer(serializers.Serializer):
    station_id = serializers.CharField()
    station_name = serializers.CharField()
    temperature_mean = serializers.FloatField()
    baseline_mean = serializers.FloatField()
    deviation = serializers.FloatField()
    lat = serializers.FloatField(allow_null=True)
    lon = serializers.FloatField(allow_null=True)
    department = serializers.CharField(allow_null=True)
    alt = serializers.FloatField(allow_null=True)
    region = serializers.CharField(allow_null=True)


class TemperatureDeviationOverviewMetadataSerializer(serializers.Serializer):
    date_start = serializers.DateField()
    date_end = serializers.DateField()
    baseline = serializers.CharField()
    filters = serializers.DictField()
    ordering = serializers.CharField()


class TemperatureDeviationOverviewResponseSerializer(serializers.Serializer):
    metadata = TemperatureDeviationOverviewMetadataSerializer()
    national = TemperatureDeviationOverviewNationalSerializer()
    pagination = PaginationMetadataSerializer()
    stations = TemperatureDeviationOverviewStationSerializer(many=True)


class NationalIndicatorKpiQuerySerializer(serializers.Serializer):
    date_start = serializers.DateField(required=True)
    date_end = serializers.DateField(required=True)
    type = serializers.ChoiceField(
        choices=["hot", "cold"], required=False, allow_null=True, default=None
    )

    def validate(self, attrs):
        if attrs["date_start"] > attrs["date_end"]:
            raise serializers.ValidationError(
                {"date_end": "date_end doit être >= date_start."}
            )
        return attrs


class NationalIndicatorKpiDaySerializer(serializers.Serializer):
    date = serializers.DateField()
    temperature = serializers.FloatField()
    baseline_mean = serializers.FloatField()
    baseline_std_dev = serializers.FloatField()


class NationalIndicatorKpiResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    itn_mean = serializers.FloatField(allow_null=True)
    deviation_from_normal = serializers.FloatField(allow_null=True)
    days = NationalIndicatorKpiDaySerializer(many=True)


class RecordsGraphQuerySerializer(serializers.Serializer):
    date_start = serializers.DateField()
    date_end = serializers.DateField()
    granularity = serializers.ChoiceField(choices=["day", "month", "year"])
    period_type = serializers.ChoiceField(
        choices=["all_time", "month", "season"],
        required=False,
        default="all_time",
    )
    type_records = serializers.ChoiceField(
        choices=["hot", "cold", "all"],
        required=False,
        default="all",
    )
    month = serializers.IntegerField(required=False, min_value=1, max_value=12)
    season = serializers.ChoiceField(
        choices=["spring", "summer", "autumn", "winter"],
        required=False,
    )
    territoire = serializers.ChoiceField(
        choices=["france", "region", "department", "station"],
        required=False,
        default="france",
    )
    territoire_id = serializers.CharField(required=False)

    def validate(self, attrs):
        period_type = attrs.get("period_type", "all_time")
        territoire = attrs.get("territoire", "france")

        if period_type == "month" and attrs.get("month") is None:
            raise serializers.ValidationError({"month": "Requis si period_type=month."})

        if period_type == "season" and attrs.get("season") is None:
            raise serializers.ValidationError(
                {"season": "Requis si period_type=season."}
            )

        if territoire != "france" and not attrs.get("territoire_id"):
            raise serializers.ValidationError(
                {"territoire_id": f"Requis si territoire={territoire}."}
            )

        return attrs


class RecordsGraphBucketSerializer(serializers.Serializer):
    bucket = serializers.CharField()
    nb_records_battus = serializers.IntegerField()


class RecordsGraphRecordSerializer(serializers.Serializer):
    date = serializers.DateField()
    station_id = serializers.CharField()
    station_name = serializers.CharField()
    type_records = serializers.ChoiceField(choices=["hot", "cold"])
    valeur = serializers.FloatField()


class RecordsGraphResponseSerializer(serializers.Serializer):
    buckets = RecordsGraphBucketSerializer(many=True)
    records = RecordsGraphRecordSerializer(many=True)
