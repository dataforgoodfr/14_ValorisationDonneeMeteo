"""
Django models for weather data.
Tables are managed by Django with TimescaleDB hypertables via custom migrations.
"""

from django.db import models


class Station(models.Model):
    """Weather station metadata."""

    code = models.CharField(max_length=8, unique=True)
    nom = models.TextField()
    departement = models.IntegerField()
    frequence = models.CharField(max_length=20, default="horaire")
    poste_ouvert = models.BooleanField(default=True)
    type_poste = models.IntegerField(default=0)
    lon = models.FloatField()
    lat = models.FloatField()
    alt = models.FloatField()
    poste_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["lat"]),
            models.Index(fields=["lon"]),
        ]

    def __str__(self) -> str:
        return f"{self.nom} ({self.code})"


class HoraireTempsReel(models.Model):
    """
    Real-time hourly weather measurements.
    TimescaleDB hypertable partitioned by validity_time.
    """

    station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name="hourly_measurements",
    )
    lat = models.FloatField()
    lon = models.FloatField()
    reference_time = models.DateTimeField()
    insert_time = models.DateTimeField()
    validity_time = models.DateTimeField(db_index=True)

    # Temperature fields (°C)
    t = models.FloatField(null=True, blank=True, help_text="Current temperature")
    td = models.FloatField(null=True, blank=True, help_text="Dew point")
    tx = models.FloatField(null=True, blank=True, help_text="Daily max temperature")
    tn = models.FloatField(null=True, blank=True, help_text="Daily min temperature")

    # Humidity (%)
    u = models.IntegerField(null=True, blank=True, help_text="Relative humidity")
    ux = models.IntegerField(null=True, blank=True, help_text="Max humidity")
    un = models.IntegerField(null=True, blank=True, help_text="Min humidity")

    # Wind
    dd = models.IntegerField(null=True, blank=True, help_text="Wind direction (°)")
    ff = models.FloatField(null=True, blank=True, help_text="Wind speed (m/s)")
    dxy = models.IntegerField(null=True, blank=True, help_text="Gust direction")
    fxy = models.FloatField(null=True, blank=True, help_text="Gust speed (m/s)")
    dxi = models.IntegerField(null=True, blank=True, help_text="Instant direction")
    fxi = models.FloatField(null=True, blank=True, help_text="Instant speed (m/s)")

    # Precipitation
    rr1 = models.FloatField(null=True, blank=True, help_text="Hourly rainfall (mm)")

    # Soil temperature at various depths (°C)
    t_10 = models.FloatField(null=True, blank=True, help_text="Soil temp at 10cm")
    t_20 = models.FloatField(null=True, blank=True, help_text="Soil temp at 20cm")
    t_50 = models.FloatField(null=True, blank=True, help_text="Soil temp at 50cm")
    t_100 = models.FloatField(null=True, blank=True, help_text="Soil temp at 100cm")

    # Other measurements
    vv = models.IntegerField(null=True, blank=True, help_text="Visibility (m)")
    etat_sol = models.IntegerField(null=True, blank=True, help_text="Ground state")
    sss = models.FloatField(null=True, blank=True, help_text="Snow depth")
    n = models.IntegerField(null=True, blank=True, help_text="Cloud cover (0-8)")
    insolh = models.FloatField(null=True, blank=True, help_text="Sunshine hours")
    ray_glo01 = models.FloatField(
        null=True, blank=True, help_text="Solar radiation (W/m²)"
    )
    pres = models.FloatField(null=True, blank=True, help_text="Station pressure (hPa)")
    pmer = models.FloatField(
        null=True, blank=True, help_text="Sea level pressure (hPa)"
    )

    class Meta:
        # Note: UniqueConstraint not used because TimescaleDB hypertables require
        # the partitioning column to be part of any unique index. We use a regular
        # index instead, managed in the migration.
        ordering = ["-validity_time"]

    def __str__(self) -> str:
        return f"{self.station.code} @ {self.validity_time}"


class Quotidienne(models.Model):
    """
    Daily aggregated weather data.
    TimescaleDB hypertable partitioned by date.
    """

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
    htn = models.CharField(
        max_length=4, null=True, blank=True, help_text="Time of min (HHMM)"
    )
    qhtn = models.IntegerField(null=True, blank=True)

    tx = models.FloatField(null=True, blank=True, help_text="Max temperature")
    qtx = models.IntegerField(null=True, blank=True)
    htx = models.CharField(
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
    hxy = models.CharField(
        max_length=4, null=True, blank=True, help_text="Time of max gust"
    )
    qhxy = models.IntegerField(null=True, blank=True)

    fxi = models.FloatField(null=True, blank=True)
    qfxi = models.IntegerField(null=True, blank=True)
    dxi = models.IntegerField(null=True, blank=True)
    qdxi = models.IntegerField(null=True, blank=True)
    hxi = models.CharField(max_length=4, null=True, blank=True)
    qhxi = models.IntegerField(null=True, blank=True)

    fxi2 = models.FloatField(null=True, blank=True)
    qfxi2 = models.IntegerField(null=True, blank=True)
    dxi2 = models.IntegerField(null=True, blank=True)
    qdxi2 = models.IntegerField(null=True, blank=True)
    hxi2 = models.CharField(max_length=4, null=True, blank=True)
    qhxi2 = models.IntegerField(null=True, blank=True)

    fxi3s = models.FloatField(null=True, blank=True)
    qfxi3s = models.IntegerField(null=True, blank=True)
    dxi3s = models.IntegerField(null=True, blank=True)
    qdxi3s = models.IntegerField(null=True, blank=True)
    hxi3s = models.CharField(max_length=4, null=True, blank=True)
    qhxi3s = models.IntegerField(null=True, blank=True)

    # Precipitation duration
    drr = models.IntegerField(
        null=True, blank=True, help_text="Precipitation duration (min)"
    )
    qdrr = models.IntegerField(null=True, blank=True)

    class Meta:
        # Note: UniqueConstraint not used because TimescaleDB hypertables require
        # the partitioning column to be part of any unique index. We use a regular
        # index instead, managed in the migration.
        ordering = ["-date"]

    def __str__(self) -> str:
        return f"{self.nom_usuel} ({self.station.code}) - {self.date}"
