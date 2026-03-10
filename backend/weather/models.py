from django.db import models


class Station(models.Model):
    station_code = models.CharField(primary_key=True, max_length=8)
    name = models.TextField()

    departement = models.IntegerField(null=True, blank=True)

    is_open = models.BooleanField(null=True, blank=True)
    station_type = models.IntegerField(null=True, blank=True)

    lon = models.FloatField(null=True, blank=True)
    lat = models.FloatField(null=True, blank=True)
    alt = models.FloatField(null=True, blank=True)

    is_public = models.BooleanField(null=True, blank=True)

    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "v_station"

    def __str__(self) -> str:
        return f"{self.name} ({self.station_code})"


class QuotidienneITN(models.Model):
    pk = models.CompositePrimaryKey("station_code", "date")

    station_code = models.CharField(max_length=8)
    date = models.DateField()
    tntxm = models.FloatField()

    class Meta:
        managed = False
        db_table = "v_quotidienne_itn"
        ordering = ["date", "station_code"]

    def __str__(self) -> str:
        return f"{self.station_code} {self.date}"
