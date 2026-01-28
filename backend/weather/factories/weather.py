"""
Factory Boy factories for weather models.
Used for testing and data population.
"""

import random
from datetime import timedelta

import factory
from django.utils import timezone

from weather.data_generators.constants import STATIONS
from weather.data_generators.weather_physics import (
    calculate_base_climate,
    generate_cloud_cover,
    generate_humidity,
    generate_precipitation,
    generate_pressure,
    generate_solar_radiation,
    generate_soil_temperatures,
    generate_sunshine_hours,
    generate_temperature_profile,
    generate_visibility,
    generate_wind,
)
from weather.models import HoraireTempsReel, Quotidienne, Station


class StationFactory(factory.django.DjangoModelFactory):
    """Factory for creating Station instances."""

    class Meta:
        model = Station
        django_get_or_create = ("code",)

    code = factory.Sequence(lambda n: STATIONS[n % len(STATIONS)][0])
    nom = factory.LazyAttribute(lambda o: next(s[1] for s in STATIONS if s[0] == o.code))
    lat = factory.LazyAttribute(lambda o: next(s[2] for s in STATIONS if s[0] == o.code))
    lon = factory.LazyAttribute(lambda o: next(s[3] for s in STATIONS if s[0] == o.code))
    alt = factory.LazyAttribute(lambda o: next(s[4] for s in STATIONS if s[0] == o.code))
    departement = factory.LazyAttribute(lambda o: next(s[5] for s in STATIONS if s[0] == o.code))
    type_poste = factory.LazyAttribute(lambda o: next(s[6] for s in STATIONS if s[0] == o.code))
    poste_public = factory.LazyAttribute(lambda o: next(s[7] for s in STATIONS if s[0] == o.code))
    poste_ouvert = factory.LazyAttribute(lambda o: next(s[8] for s in STATIONS if s[0] == o.code))
    frequence = "horaire"

    @classmethod
    def create_all_stations(cls) -> list[Station]:
        """Create all predefined French weather stations."""
        stations = []
        for station_data in STATIONS:
            station = cls.create(
                code=station_data[0],
                nom=station_data[1],
                lat=station_data[2],
                lon=station_data[3],
                alt=station_data[4],
                departement=station_data[5],
                type_poste=station_data[6],
                poste_public=station_data[7],
                poste_ouvert=station_data[8],
            )
            stations.append(station)
        return stations


class HoraireTempsReelFactory(factory.django.DjangoModelFactory):
    """Factory for creating hourly weather measurements."""

    class Meta:
        model = HoraireTempsReel

    station = factory.SubFactory(StationFactory)
    validity_time = factory.LazyFunction(lambda: timezone.now().replace(minute=0, second=0, microsecond=0))
    reference_time = factory.LazyAttribute(lambda o: o.validity_time)
    insert_time = factory.LazyAttribute(lambda o: o.validity_time)

    lat = factory.LazyAttribute(lambda o: o.station.lat)
    lon = factory.LazyAttribute(lambda o: o.station.lon)

    # Temperature
    t = factory.LazyAttribute(
        lambda o: round(
            generate_temperature_profile(
                o.validity_time.hour,
                calculate_base_climate(o.station.lat, o.station.alt)["base_temp"],
            )
            + random.gauss(0, 1.5),
            1,
        )
    )
    td = factory.LazyAttribute(lambda o: round(o.t - random.uniform(2, 8), 1))

    # Humidity
    u = factory.LazyAttribute(
        lambda o: generate_humidity(
            calculate_base_climate(o.station.lat, o.station.alt)["humidity_base"],
            o.t - calculate_base_climate(o.station.lat, o.station.alt)["base_temp"],
        )[0]
    )
    ux = factory.LazyAttribute(lambda o: min(o.u + random.randint(5, 15), 100))
    un = factory.LazyAttribute(lambda o: max(o.u - random.randint(5, 15), 30))

    # Wind
    dd = factory.LazyFunction(lambda: random.randint(0, 360))
    ff = factory.LazyFunction(lambda: round(abs(random.gauss(3, 2)), 1))
    dxy = factory.LazyAttribute(lambda o: o.dd)
    fxy = factory.LazyAttribute(lambda o: round(o.ff + random.uniform(2, 8), 1))
    dxi = factory.LazyAttribute(lambda o: o.dd)
    fxi = factory.LazyAttribute(lambda o: round(o.ff + random.uniform(-1, 3), 1))

    # Precipitation
    rr1 = factory.LazyFunction(generate_precipitation)

    # Other measurements
    vv = factory.LazyAttribute(lambda o: generate_visibility(o.rr1))
    n = factory.LazyAttribute(lambda o: generate_cloud_cover(o.rr1 > 0))
    insolh = factory.LazyAttribute(lambda o: generate_sunshine_hours(o.validity_time.hour, o.n))
    ray_glo01 = factory.LazyAttribute(lambda o: generate_solar_radiation(o.validity_time.hour, o.n))

    # Pressure
    pres = factory.LazyAttribute(lambda o: generate_pressure(o.station.alt)[0])
    pmer = factory.LazyAttribute(lambda o: generate_pressure(o.station.alt)[1])

    # Soil temperatures
    t_10 = factory.LazyAttribute(lambda o: generate_soil_temperatures(o.t)[0])
    t_20 = factory.LazyAttribute(lambda o: generate_soil_temperatures(o.t)[1])
    t_50 = factory.LazyAttribute(lambda o: generate_soil_temperatures(o.t)[2])
    t_100 = factory.LazyAttribute(lambda o: generate_soil_temperatures(o.t)[3])

    etat_sol = 0
    sss = None

    class Params:
        """Traits for different weather scenarios."""

        rainy = factory.Trait(
            rr1=factory.LazyFunction(lambda: round(random.uniform(5, 20), 1)),
            n=factory.LazyFunction(lambda: random.randint(5, 8)),
            vv=factory.LazyFunction(lambda: random.randint(1000, 5000)),
        )
        sunny = factory.Trait(
            rr1=0,
            n=factory.LazyFunction(lambda: random.randint(0, 2)),
            vv=10000,
            insolh=factory.LazyFunction(lambda: round(random.uniform(0.7, 1.0), 2)),
        )


class QuotidienneFactory(factory.django.DjangoModelFactory):
    """Factory for creating daily aggregated weather data."""

    class Meta:
        model = Quotidienne

    station = factory.SubFactory(StationFactory)
    date = factory.LazyFunction(lambda: timezone.now().date() - timedelta(days=random.randint(0, 30)))

    nom_usuel = factory.LazyAttribute(lambda o: o.station.nom)
    lat = factory.LazyAttribute(lambda o: o.station.lat)
    lon = factory.LazyAttribute(lambda o: o.station.lon)
    alti = factory.LazyAttribute(lambda o: o.station.alt)

    # Temperature
    tn = factory.LazyFunction(lambda: round(random.uniform(0, 10), 1))
    tx = factory.LazyFunction(lambda: round(random.uniform(15, 25), 1))
    tm = factory.LazyAttribute(lambda o: round((o.tn + o.tx) / 2, 1))
    tntxm = factory.LazyAttribute(lambda o: round((o.tn + o.tx) / 2, 1))
    tampli = factory.LazyAttribute(lambda o: round(o.tx - o.tn, 1))
    qtn = 1
    qtx = 1
    qtm = 1
    qtntxm = 1
    qtampli = 1
    htn = factory.LazyFunction(lambda: f"{random.randint(4, 8):02d}00")
    htx = factory.LazyFunction(lambda: f"{random.randint(13, 17):02d}00")
    qhtn = 1
    qhtx = 1

    # Rainfall
    rr = factory.LazyFunction(lambda: round(random.uniform(0, 10), 1) if random.random() < 0.3 else 0)
    qrr = 1

    # Wind
    ffm = factory.LazyFunction(lambda: round(random.uniform(2, 8), 1))
    qffm = 1
    fxy = factory.LazyFunction(lambda: round(random.uniform(10, 25), 1))
    qfxy = 1
    dxy = factory.LazyFunction(lambda: random.randint(0, 360))
    qdxy = 1
    hxy = factory.LazyFunction(lambda: f"{random.randint(0, 23):02d}{random.randint(0, 5) * 10:02d}")
    qhxy = 1
