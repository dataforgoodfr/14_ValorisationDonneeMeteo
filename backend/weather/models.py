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

    station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name="daily_measurements",
    )
    nom_usuel = models.TextField()
    lat = models.FloatField()
    lon = models.FloatField()
    alti = models.FloatField()
    date = models.DateField(db_index=True)

    # Rainfall
    rr = models.FloatField(null=True, blank=True, help_text="Daily rainfall (mm)")
    qrr = models.IntegerField(null=True, blank=True, help_text="Quality flag")

    # Temperature
    tn = models.FloatField(null=True, blank=True, help_text="Min temperature")
    qtn = models.IntegerField(null=True, blank=True)
    htn = models.CharField(  # noqa: DJ001
        max_length=4, null=True, blank=True, help_text="Time of min (HHMM)"
    )
    qhtn = models.IntegerField(null=True, blank=True)

    tx = models.FloatField(null=True, blank=True, help_text="Max temperature")
    qtx = models.IntegerField(null=True, blank=True)
    htx = models.CharField(  # noqa: DJ001
        max_length=4, null=True, blank=True, help_text="Time of max (HHMM)"
    )
    qhtx = models.IntegerField(null=True, blank=True)

    tm = models.FloatField(null=True, blank=True, help_text="Mean temperature")
    qtm = models.IntegerField(null=True, blank=True)

    tntxm = models.FloatField(null=True, blank=True, help_text="(TN+TX)/2")
    qtntxm = models.IntegerField(null=True, blank=True)

    tampli = models.FloatField(null=True, blank=True, help_text="Temperature amplitude")
    qtampli = models.IntegerField(null=True, blank=True)

    # Soil temperature
    tnsol = models.FloatField(null=True, blank=True, help_text="Min ground temp")
    qtnsol = models.IntegerField(null=True, blank=True)

    tn50 = models.FloatField(null=True, blank=True, help_text="Min temp at 50cm")
    qtn50 = models.IntegerField(null=True, blank=True)

    # Degree days
    dg = models.IntegerField(null=True, blank=True, help_text="Degree days")
    qdg = models.IntegerField(null=True, blank=True)

    # Wind
    ffm = models.FloatField(null=True, blank=True, help_text="Mean wind speed")
    qffm = models.IntegerField(null=True, blank=True)

    ff2m = models.FloatField(null=True, blank=True, help_text="Mean wind at 2m")
    qff2m = models.IntegerField(null=True, blank=True)

    fxy = models.FloatField(null=True, blank=True, help_text="Max gust speed")
    qfxy = models.IntegerField(null=True, blank=True)
    dxy = models.IntegerField(null=True, blank=True, help_text="Max gust direction")
    qdxy = models.IntegerField(null=True, blank=True)
    hxy = models.CharField(  # noqa: DJ001
        max_length=4, null=True, blank=True, help_text="Time of max gust"
    )
    qhxy = models.IntegerField(null=True, blank=True)

    fxi = models.FloatField(null=True, blank=True)
    qfxi = models.IntegerField(null=True, blank=True)
    dxi = models.IntegerField(null=True, blank=True)
    qdxi = models.IntegerField(null=True, blank=True)
    hxi = models.CharField(max_length=4, null=True, blank=True)  # noqa: DJ001
    qhxi = models.IntegerField(null=True, blank=True)

    fxi2 = models.FloatField(null=True, blank=True)
    qfxi2 = models.IntegerField(null=True, blank=True)
    dxi2 = models.IntegerField(null=True, blank=True)
    qdxi2 = models.IntegerField(null=True, blank=True)
    hxi2 = models.CharField(max_length=4, null=True, blank=True)  # noqa: DJ001
    qhxi2 = models.IntegerField(null=True, blank=True)

    fxi3s = models.FloatField(null=True, blank=True)
    qfxi3s = models.IntegerField(null=True, blank=True)
    dxi3s = models.IntegerField(null=True, blank=True)
    qdxi3s = models.IntegerField(null=True, blank=True)
    hxi3s = models.CharField(max_length=4, null=True, blank=True)  # noqa: DJ001
    qhxi3s = models.IntegerField(null=True, blank=True)

    # Precipitation duration
    drr = models.IntegerField(
        null=True, blank=True, help_text="Precipitation duration (min)"
    )
    qdrr = models.IntegerField(null=True, blank=True)
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
