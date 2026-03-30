import datetime as dt

from django.db import models


class TimestampAsDateField(models.DateField):
    """DateField that maps a SQL timestamp column to a Python date.

    - from_db_value: datetime → date (reading)
    - get_prep_value: date → datetime (writing/filtering)
    """

    def from_db_value(
        self,
        value,
        expression,
        connection,
    ) -> dt.date | None:
        if isinstance(value, dt.datetime):
            return value.date()
        return value

    def get_prep_value(self, value) -> dt.datetime | None:
        value = super().get_prep_value(value)
        if isinstance(value, dt.date) and not isinstance(value, dt.datetime):
            return dt.datetime.combine(value, dt.time.min)
        return value


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
    date = TimestampAsDateField()
    tntxm = models.FloatField()

    class Meta:
        managed = False
        db_table = "v_quotidienne_itn"
        ordering = ["date", "station_code"]

    def __str__(self) -> str:
        return f"{self.station_code} {self.date}"


class BaselineStationDailyMean19912020(models.Model):
    pk = models.CompositePrimaryKey("station_code", "month", "day")

    station_code = models.CharField(max_length=8)
    month = models.IntegerField()
    day = models.IntegerField()
    sample_count = models.IntegerField()
    baseline_mean_tntxm = models.FloatField()

    class Meta:
        managed = False
        db_table = "baseline_station_daily_mean_1991_2020"
        ordering = ["station_code", "month", "day"]

    def __str__(self) -> str:
        return f"{self.station_code} {self.month:02d}-{self.day:02d}"
