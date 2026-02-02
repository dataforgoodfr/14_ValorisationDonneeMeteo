"""
Django management command to populate weather mock data.
Generates realistic French weather station data for development and testing.
"""

import random
from datetime import timedelta

import numpy as np
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, models
from django.utils import timezone

from weather.data_generators.constants import (
    DEFAULT_BATCH_SIZE,
    DEFAULT_DAYS,
    NUMPY_SEED,
    RANDOM_SEED,
    STATIONS,
)
from weather.data_generators.weather_physics import (
    calculate_base_climate,
    generate_cloud_cover,
    generate_humidity,
    generate_precipitation,
    generate_pressure,
    generate_soil_temperatures,
    generate_solar_radiation,
    generate_sunshine_hours,
    generate_temperature_profile,
    generate_visibility,
    generate_wind,
)
from weather.models import HoraireTempsReel, Quotidienne, Station


class Command(BaseCommand):
    help = "Generate realistic mock weather data for development and testing"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=DEFAULT_DAYS,
            help=f"Number of days of data to generate (default: {DEFAULT_DAYS})",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=DEFAULT_BATCH_SIZE,
            help=f"Batch size for bulk inserts (default: {DEFAULT_BATCH_SIZE})",
        )
        parser.add_argument(
            "--seed",
            type=int,
            default=RANDOM_SEED,
            help=f"Random seed for reproducibility (default: {RANDOM_SEED})",
        )
        parser.add_argument(
            "--stations-only",
            action="store_true",
            help="Only generate station data",
        )
        parser.add_argument(
            "--skip-daily",
            action="store_true",
            help="Skip daily aggregation",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing data before generating",
        )

    def handle(self, *args, **options):
        # Safety check: refuse to run in production
        if not settings.DEBUG:
            raise CommandError(
                "This command is only available in development (DEBUG=True). "
                "It is not safe to run in production as it can delete data."
            )

        # Set seeds for reproducibility
        random.seed(options["seed"])
        np.random.seed(options["seed"])

        verbosity = options["verbosity"]

        if options["clear"]:
            self._clear_data(verbosity)

        self.stdout.write("Generating stations...")
        stations = self._generate_stations(verbosity)

        if options["stations_only"]:
            self.stdout.write(self.style.SUCCESS("Station generation complete!"))
            return

        self.stdout.write("Generating hourly data (this may take a moment)...")
        hourly_count = self._generate_hourly_data(
            stations=stations,
            days=options["days"],
            batch_size=options["batch_size"],
            verbosity=verbosity,
        )
        self.stdout.write(f"  Inserted {hourly_count} hourly records")

        if not options["skip_daily"]:
            self.stdout.write("Generating daily aggregations...")
            daily_count = self._generate_daily_data(verbosity)
            self.stdout.write(f"  Inserted {daily_count} daily records")

        self._display_summary()
        self.stdout.write(self.style.SUCCESS("Mock data generation complete!"))

    def _clear_data(self, verbosity):
        """Clear existing weather data."""
        if verbosity > 0:
            self.stdout.write("Clearing existing data...")
        Quotidienne.objects.all().delete()
        HoraireTempsReel.objects.all().delete()
        Station.objects.all().delete()

    def _generate_stations(self, verbosity) -> list[Station]:
        """Insert station metadata."""
        stations = []

        for station_data in STATIONS:
            code, name, lat, lon, alt, dept, type_poste, public, ouvert = station_data
            station, created = Station.objects.get_or_create(
                code=code,
                defaults={
                    "nom": name,
                    "lat": lat,
                    "lon": lon,
                    "alt": alt,
                    "departement": dept,
                    "type_poste": type_poste,
                    "poste_public": public,
                    "poste_ouvert": ouvert,
                    "frequence": "horaire",
                },
            )
            stations.append(station)

        if verbosity > 0:
            self.stdout.write(f"  Created/verified {len(stations)} stations")

        return stations

    def _generate_hourly_data(
        self,
        stations: list[Station],
        days: int,
        batch_size: int,
        verbosity: int,
    ) -> int:
        """Generate hourly weather data."""
        end_time = timezone.now().replace(minute=0, second=0, microsecond=0)
        start_time = end_time - timedelta(days=days)

        total_inserted = 0
        batch = []

        for station in stations:
            climate = calculate_base_climate(station.lat, station.alt)
            current_time = start_time
            wind_direction = random.randint(0, 360)

            # Track daily extremes
            daily_tx = None
            daily_tn = None

            while current_time <= end_time:
                hour = current_time.hour

                # Reset daily extremes at midnight
                if hour == 0:
                    daily_tx = None
                    daily_tn = None

                # Temperature with diurnal cycle
                temp = round(
                    generate_temperature_profile(hour, climate["base_temp"])
                    + random.gauss(0, 1.5),
                    1,
                )
                temp_dew = round(temp - random.uniform(2, 8), 1)

                # Track daily extremes
                if daily_tx is None or temp > daily_tx:
                    daily_tx = temp
                if daily_tn is None or temp < daily_tn:
                    daily_tn = temp

                # Humidity
                humidity, humidity_max, humidity_min = generate_humidity(
                    climate["humidity_base"],
                    temp - climate["base_temp"],
                )

                # Wind
                wind = generate_wind(wind_direction)
                wind_direction = wind["direction"]

                # Precipitation
                rain = generate_precipitation()

                # Other measurements
                visibility = generate_visibility(rain)
                clouds = generate_cloud_cover(rain > 0)
                radiation = generate_solar_radiation(hour, clouds)
                sunshine = generate_sunshine_hours(hour, clouds)
                pres, pmer = generate_pressure(station.alt)
                t_10, t_20, t_50, t_100 = generate_soil_temperatures(temp)

                batch.append(
                    HoraireTempsReel(
                        station=station,
                        lat=station.lat,
                        lon=station.lon,
                        reference_time=current_time,
                        insert_time=current_time,
                        validity_time=current_time,
                        t=temp,
                        td=temp_dew,
                        tx=daily_tx,
                        tn=daily_tn,
                        u=humidity,
                        ux=humidity_max,
                        un=humidity_min,
                        dd=wind["direction"],
                        ff=wind["speed"],
                        dxy=wind["direction"],
                        fxy=wind["gust"],
                        dxi=wind["direction"],
                        fxi=wind["instant"],
                        rr1=rain if rain > 0 else 0,
                        t_10=t_10,
                        t_20=t_20,
                        t_50=t_50,
                        t_100=t_100,
                        vv=visibility,
                        etat_sol=0,
                        sss=None,
                        n=clouds,
                        insolh=sunshine,
                        ray_glo01=radiation,
                        pres=pres,
                        pmer=pmer,
                    )
                )

                # Batch insert
                if len(batch) >= batch_size:
                    HoraireTempsReel.objects.bulk_create(batch, ignore_conflicts=True)
                    total_inserted += len(batch)
                    if verbosity > 1:
                        self.stdout.write(f"  Inserted batch ({total_inserted} total)")
                    batch = []

                current_time += timedelta(hours=1)

        # Insert remaining records
        if batch:
            HoraireTempsReel.objects.bulk_create(batch, ignore_conflicts=True)
            total_inserted += len(batch)

        return total_inserted

    def _generate_daily_data(self, verbosity: int) -> int:
        """Generate daily aggregations using SQL for efficiency."""
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO weather_quotidienne (
                    station_id, nom_usuel, lat, lon, alti, date,
                    rr, qrr, tn, qtn, htn, qhtn, tx, qtx, htx, qhtx,
                    tm, qtm, tntxm, qtntxm, tampli, qtampli,
                    ffm, qffm, fxy, qfxy, dxy, qdxy, hxy, qhxy
                )
                SELECT
                    h.station_id,
                    s.nom AS nom_usuel,
                    h.lat,
                    h.lon,
                    s.alt AS alti,
                    DATE(h.validity_time) AS date,
                    ROUND(SUM(COALESCE(h.rr1, 0))::numeric, 1) AS rr,
                    1 AS qrr,
                    ROUND(MIN(h.t)::numeric, 1) AS tn,
                    1 AS qtn,
                    TO_CHAR(
                        (ARRAY_AGG(h.validity_time ORDER BY h.t ASC))[1],
                        'HH24MI'
                    ) AS htn,
                    1 AS qhtn,
                    ROUND(MAX(h.t)::numeric, 1) AS tx,
                    1 AS qtx,
                    TO_CHAR(
                        (ARRAY_AGG(h.validity_time ORDER BY h.t DESC))[1],
                        'HH24MI'
                    ) AS htx,
                    1 AS qhtx,
                    ROUND(AVG(h.t)::numeric, 1) AS tm,
                    1 AS qtm,
                    ROUND(((MIN(h.t) + MAX(h.t)) / 2)::numeric, 1) AS tntxm,
                    1 AS qtntxm,
                    ROUND((MAX(h.t) - MIN(h.t))::numeric, 1) AS tampli,
                    1 AS qtampli,
                    ROUND(AVG(h.ff)::numeric, 1) AS ffm,
                    1 AS qffm,
                    ROUND(MAX(h.fxy)::numeric, 1) AS fxy,
                    1 AS qfxy,
                    (ARRAY_AGG(h.dxy ORDER BY h.fxy DESC))[1] AS dxy,
                    1 AS qdxy,
                    TO_CHAR(
                        (ARRAY_AGG(h.validity_time ORDER BY h.fxy DESC))[1],
                        'HH24MI'
                    ) AS hxy,
                    1 AS qhxy
                FROM weather_horairetempsreel h
                JOIN weather_station s ON h.station_id = s.id
                WHERE s.frequence = 'horaire'
                GROUP BY h.station_id, s.nom, h.lat, h.lon, s.alt, DATE(h.validity_time)
                ON CONFLICT DO NOTHING
            """
            )
            return cursor.rowcount

    def _display_summary(self):
        """Display data generation summary."""
        station_count = Station.objects.count()
        hourly_count = HoraireTempsReel.objects.count()
        daily_count = Quotidienne.objects.count()

        # Get time range if data exists
        time_range = HoraireTempsReel.objects.aggregate(
            min_time=models.Min("validity_time"),
            max_time=models.Max("validity_time"),
        )

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("MOCK DATA GENERATION SUMMARY")
        self.stdout.write("=" * 60)
        self.stdout.write(f"Stations created:       {station_count}")
        self.stdout.write(f"Hourly records:         {hourly_count}")
        self.stdout.write(f"Daily records:          {daily_count}")
        if time_range["min_time"] and time_range["max_time"]:
            self.stdout.write(
                f"Time range:             {time_range['min_time']} to {time_range['max_time']}"
            )
        self.stdout.write("=" * 60)
