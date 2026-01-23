"""
Django models for existing TimescaleDB weather tables.
These models use managed=False since the tables already exist.
"""

from django.db import models


class Station(models.Model):
    """Weather station metadata."""

    id = models.CharField(max_length=8, primary_key=True)
    nom = models.TextField()
    departement = models.IntegerField()
    frequence = models.TextField()
    poste_ouvert = models.BooleanField(db_column="posteOuvert")
    type_poste = models.IntegerField(db_column="typePoste")
    lon = models.FloatField()
    lat = models.FloatField()
    alt = models.FloatField()
    poste_public = models.BooleanField(db_column="postePublic")
    created_at = models.DateTimeField(db_column="createdAt")
    updated_at = models.DateTimeField(db_column="updatedAt")

    class Meta:
        managed = False
        db_table = "Station"

    def __str__(self) -> str:
        return f"{self.nom} ({self.id})"


class HoraireTempsReel(models.Model):
    """
    Real-time hourly weather measurements.
    TimescaleDB hypertable partitioned by validity_time.
    """

    geo_id_insee = models.CharField(max_length=8, primary_key=True)
    lat = models.FloatField()
    lon = models.FloatField()
    reference_time = models.DateTimeField()
    insert_time = models.DateTimeField()
    validity_time = models.DateTimeField()

    # Temperature fields
    t = models.FloatField(null=True, blank=True)
    td = models.FloatField(null=True, blank=True)
    tx = models.FloatField(null=True, blank=True)
    tn = models.FloatField(null=True, blank=True)

    # Humidity
    u = models.IntegerField(null=True, blank=True)
    ux = models.IntegerField(null=True, blank=True)
    un = models.IntegerField(null=True, blank=True)

    # Wind
    dd = models.IntegerField(null=True, blank=True)
    ff = models.FloatField(null=True, blank=True)
    dxy = models.IntegerField(null=True, blank=True)
    fxy = models.FloatField(null=True, blank=True)
    dxi = models.IntegerField(null=True, blank=True)
    fxi = models.FloatField(null=True, blank=True)

    # Precipitation
    rr1 = models.FloatField(null=True, blank=True)

    # Soil temperature at various depths
    t_10 = models.FloatField(null=True, blank=True)
    t_20 = models.FloatField(null=True, blank=True)
    t_50 = models.FloatField(null=True, blank=True)
    t_100 = models.FloatField(null=True, blank=True)

    # Other measurements
    vv = models.IntegerField(null=True, blank=True)
    etat_sol = models.IntegerField(null=True, blank=True)
    sss = models.FloatField(null=True, blank=True)
    n = models.IntegerField(null=True, blank=True)
    insolh = models.FloatField(null=True, blank=True)
    ray_glo01 = models.FloatField(null=True, blank=True)
    pres = models.FloatField(null=True, blank=True)
    pmer = models.FloatField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "HoraireTempsReel"
        ordering = ["-validity_time"]

    def __str__(self) -> str:
        return f"{self.geo_id_insee} @ {self.validity_time}"


class Quotidienne(models.Model):
    """
    Daily aggregated weather data.
    TimescaleDB hypertable partitioned by AAAAMMJJ.
    """

    num_poste = models.CharField(max_length=8, primary_key=True, db_column="NUM_POSTE")
    nom_usuel = models.TextField(db_column="NOM_USUEL")
    lat = models.FloatField(db_column="LAT")
    lon = models.FloatField(db_column="LON")
    alti = models.FloatField(db_column="ALTI")
    date = models.DateTimeField(db_column="AAAAMMJJ")

    # Rainfall
    rr = models.FloatField(null=True, blank=True, db_column="RR")
    qrr = models.IntegerField(null=True, blank=True, db_column="QRR")

    # Temperature
    tn = models.FloatField(null=True, blank=True, db_column="TN")
    qtn = models.IntegerField(null=True, blank=True, db_column="QTN")
    htn = models.CharField(max_length=4, null=True, blank=True, db_column="HTN")
    qhtn = models.IntegerField(null=True, blank=True, db_column="QHTN")

    tx = models.FloatField(null=True, blank=True, db_column="TX")
    qtx = models.IntegerField(null=True, blank=True, db_column="QTX")
    htx = models.CharField(max_length=4, null=True, blank=True, db_column="HTX")
    qhtx = models.IntegerField(null=True, blank=True, db_column="QHTX")

    tm = models.FloatField(null=True, blank=True, db_column="TM")
    qtm = models.IntegerField(null=True, blank=True, db_column="QTM")

    tntxm = models.FloatField(null=True, blank=True, db_column="TNTXM")
    qtntxm = models.IntegerField(null=True, blank=True, db_column="QTNTXM")

    tampli = models.FloatField(null=True, blank=True, db_column="TAMPLI")
    qtampli = models.IntegerField(null=True, blank=True, db_column="QTAMPLI")

    # Soil temperature
    tnsol = models.FloatField(null=True, blank=True, db_column="TNSOL")
    qtnsol = models.IntegerField(null=True, blank=True, db_column="QTNSOL")

    tn50 = models.FloatField(null=True, blank=True, db_column="TN50")
    qtn50 = models.IntegerField(null=True, blank=True, db_column="QTN50")

    # Degree days
    dg = models.IntegerField(null=True, blank=True, db_column="DG")
    qdg = models.IntegerField(null=True, blank=True, db_column="QDG")

    # Wind
    ffm = models.FloatField(null=True, blank=True, db_column="FFM")
    qffm = models.IntegerField(null=True, blank=True, db_column="QFFM")

    ff2m = models.FloatField(null=True, blank=True, db_column="FF2M")
    qff2m = models.IntegerField(null=True, blank=True, db_column="QFF2M")

    fxy = models.FloatField(null=True, blank=True, db_column="FXY")
    qfxy = models.IntegerField(null=True, blank=True, db_column="QFXY")
    dxy = models.IntegerField(null=True, blank=True, db_column="DXY")
    qdxy = models.IntegerField(null=True, blank=True, db_column="QDXY")
    hxy = models.CharField(max_length=4, null=True, blank=True, db_column="HXY")
    qhxy = models.IntegerField(null=True, blank=True, db_column="QHXY")

    fxi = models.FloatField(null=True, blank=True, db_column="FXI")
    qfxi = models.IntegerField(null=True, blank=True, db_column="QFXI")
    dxi = models.IntegerField(null=True, blank=True, db_column="DXI")
    qdxi = models.IntegerField(null=True, blank=True, db_column="QDXI")
    hxi = models.CharField(max_length=4, null=True, blank=True, db_column="HXI")
    qhxi = models.IntegerField(null=True, blank=True, db_column="QHXI")

    fxi2 = models.FloatField(null=True, blank=True, db_column="FXI2")
    qfxi2 = models.IntegerField(null=True, blank=True, db_column="QFXI2")
    dxi2 = models.IntegerField(null=True, blank=True, db_column="DXI2")
    qdxi2 = models.IntegerField(null=True, blank=True, db_column="QDXI2")
    hxi2 = models.CharField(max_length=4, null=True, blank=True, db_column="HXI2")
    qhxi2 = models.IntegerField(null=True, blank=True, db_column="QHXI2")

    fxi3s = models.FloatField(null=True, blank=True, db_column="FXI3S")
    qfxi3s = models.IntegerField(null=True, blank=True, db_column="QFXI3S")
    dxi3s = models.IntegerField(null=True, blank=True, db_column="DXI3S")
    qdxi3s = models.IntegerField(null=True, blank=True, db_column="QDXI3S")
    hxi3s = models.CharField(max_length=4, null=True, blank=True, db_column="HXI3S")
    qhxi3s = models.IntegerField(null=True, blank=True, db_column="QHXI3S")

    # Precipitation duration
    drr = models.IntegerField(null=True, blank=True, db_column="DRR")
    qdrr = models.IntegerField(null=True, blank=True, db_column="QDRR")

    class Meta:
        managed = False
        db_table = "Quotidienne"
        ordering = ["-date"]

    def __str__(self) -> str:
        return f"{self.nom_usuel} ({self.num_poste}) - {self.date}"
