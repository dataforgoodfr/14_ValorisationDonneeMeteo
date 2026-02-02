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
