"""
Weather data generation algorithms with realistic physical correlations.
All functions return Python native types (not numpy types) for database compatibility.
"""

import random

import numpy as np


def generate_temperature_profile(
    hour: int, base_temp: float, amplitude: float = 5.0
) -> float:
    """
    Generate realistic diurnal temperature variation.
    Temperature is lowest at 6 AM, highest around 3 PM.

    Args:
        hour: Hour of the day (0-23)
        base_temp: Base temperature for the location
        amplitude: Temperature swing (default 5°C)

    Returns:
        Temperature in Celsius as Python float
    """
    hour_rad = (hour - 6) * 2 * np.pi / 24
    return float(base_temp + amplitude * np.sin(hour_rad))


def calculate_base_climate(lat: float, alt: float) -> dict:
    """
    Calculate base climate parameters for a location.
    Warmer in south, cooler at altitude.

    Args:
        lat: Latitude in degrees
        alt: Altitude in meters

    Returns:
        Dictionary with base_temp and humidity_base
    """
    return {
        "base_temp": float(5 + (50 - lat) * 0.8 - alt * 0.006),
        "humidity_base": float(70 + (lat - 45) * 2),
    }


def generate_humidity(base: float, temp_deviation: float) -> tuple[int, int, int]:
    """
    Generate correlated humidity values.
    Humidity is inversely correlated with temperature.

    Args:
        base: Base humidity for the location
        temp_deviation: Temperature deviation from base

    Returns:
        Tuple of (current, max, min) humidity as integers
    """
    humidity = int(np.clip(base - temp_deviation * 2 + random.gauss(0, 5), 30, 100))
    humidity_max = min(humidity + random.randint(5, 15), 100)
    humidity_min = max(humidity - random.randint(5, 15), 30)
    return (humidity, humidity_max, humidity_min)


def generate_wind(previous_direction: int) -> dict:
    """
    Generate wind data with slow direction changes.

    Args:
        previous_direction: Previous wind direction in degrees

    Returns:
        Dictionary with direction, speed, gust, instant values
    """
    direction = (previous_direction + random.randint(-10, 10)) % 360
    speed = float(abs(random.gauss(3, 2)))
    return {
        "direction": direction,
        "speed": round(speed, 1),
        "gust": round(speed + random.uniform(2, 8), 1),
        "instant": round(speed + random.uniform(-1, 3), 1),
    }


def generate_precipitation() -> float:
    """
    Generate precipitation with 20% chance of rain.

    Returns:
        Precipitation in mm (0 if no rain)
    """
    if random.random() < 0.2:
        return round(random.uniform(0, 20), 1)
    return 0.0


def generate_pressure(alt: float) -> tuple[float, float]:
    """
    Generate station and sea-level pressure.

    Args:
        alt: Altitude in meters

    Returns:
        Tuple of (station_pressure, sea_level_pressure) in hPa
    """
    pressure_station = round(1013 + random.gauss(0, 15), 1)
    pressure_sea = round(pressure_station + alt * 0.12, 1)
    return (pressure_station, pressure_sea)


def generate_visibility(rain: float) -> int:
    """
    Generate visibility based on precipitation.
    Reduced visibility during rain.

    Args:
        rain: Precipitation amount in mm

    Returns:
        Visibility in meters
    """
    if rain < 1:
        return 10000
    return int(max(1000, 10000 - rain * 500))


def generate_cloud_cover(is_raining: bool) -> int:
    """
    Generate cloud cover correlated with rain.

    Args:
        is_raining: Whether it is currently raining

    Returns:
        Cloud cover on 0-8 scale (oktas)
    """
    base = random.gauss(4, 3)
    if is_raining:
        base += 3
    return int(np.clip(base, 0, 8))


def generate_solar_radiation(hour: int, clouds: int) -> float | None:
    """
    Generate solar radiation based on hour and cloud cover.

    Args:
        hour: Hour of the day (0-23)
        clouds: Cloud cover (0-8)

    Returns:
        Solar radiation in W/m² or None if night
    """
    if 6 <= hour <= 20:
        radiation = max(
            0,
            800 * np.sin((hour - 6) * np.pi / 14) * (1 - clouds / 10)
            + random.gauss(0, 50),
        )
        return round(float(radiation), 0) if radiation > 0 else None
    return None


def generate_sunshine_hours(hour: int, clouds: int) -> float:
    """
    Generate sunshine fraction for the hour.

    Args:
        hour: Hour of the day (0-23)
        clouds: Cloud cover (0-8)

    Returns:
        Sunshine hours (0-1)
    """
    if 6 <= hour <= 20:
        return round(max(0, 1 - clouds / 8), 2)
    return 0.0


def generate_soil_temperatures(air_temp: float) -> tuple[float, float, float, float]:
    """
    Generate soil temperatures at various depths.
    Soil temperature lags and is damped from air temperature.

    Args:
        air_temp: Air temperature in Celsius

    Returns:
        Tuple of temperatures at (10cm, 20cm, 50cm, 100cm)
    """
    return (
        round(air_temp - 2 + random.gauss(0, 0.5), 1),
        round(air_temp - 3 + random.gauss(0, 0.5), 1),
        round(air_temp - 4 + random.gauss(0, 0.5), 1),
        round(air_temp - 5 + random.gauss(0, 0.5), 1),
    )
