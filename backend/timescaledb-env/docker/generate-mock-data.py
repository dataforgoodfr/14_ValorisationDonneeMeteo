#!/usr/bin/env python3
"""
Generate realistic mock weather data for TimescaleDB
Creates 15 French weather stations with 1 month of hourly and daily data
"""

import psycopg2
from psycopg2.extras import execute_batch
from datetime import datetime, timedelta
import random
import numpy as np
from typing import List, Tuple

# Register numpy types with psycopg2 so they are converted to Python types
psycopg2.extensions.register_adapter(np.float64, lambda x: psycopg2.extensions.AsIs(float(x)))
psycopg2.extensions.register_adapter(np.float32, lambda x: psycopg2.extensions.AsIs(float(x)))
psycopg2.extensions.register_adapter(np.int64, lambda x: psycopg2.extensions.AsIs(int(x)))
psycopg2.extensions.register_adapter(np.int32, lambda x: psycopg2.extensions.AsIs(int(x)))

# Database connection parameters
DB_PARAMS = {
    'host': 'localhost',
    'port': 5432,
    'database': 'meteodb',
    'user': 'infoclimat',
    'password': 'infoclimat2026'
}

# Set random seed for reproducibility
random.seed(42)
np.random.seed(42)

# French weather stations with realistic coordinates
STATIONS = [
    # (id, name, lat, lon, alt, dept, type, public, open)
    ('75114001', 'Paris-Montsouris', 48.8217, 2.3378, 75, 75, 0, True, True),
    ('69123001', 'Lyon-Bron', 45.7272, 4.9444, 200, 69, 0, True, True),
    ('13055001', 'Marseille-Marignane', 43.4356, 5.2148, 25, 13, 0, True, True),
    ('33063001', 'Bordeaux-Mérignac', 44.8344, -0.6953, 47, 33, 0, True, True),
    ('59343001', 'Lille-Lesquin', 50.5706, 3.0994, 47, 59, 0, True, True),
    ('31555001', 'Toulouse-Blagnac', 43.6289, 1.3678, 151, 31, 0, True, True),
    ('44109001', 'Nantes-Bouguenais', 47.1531, -1.6106, 26, 44, 0, True, True),
    ('67482001', 'Strasbourg-Entzheim', 48.5439, 7.6281, 150, 67, 0, True, True),
    ('29075001', 'Brest-Guipavas', 48.4478, -4.4186, 94, 29, 0, True, True),
    ('06088001', 'Nice-Côte d\'Azur', 43.6584, 7.2158, 4, 6, 0, True, True),
    ('74010001', 'Chamonix', 45.9236, 6.8714, 1042, 74, 0, True, True),
    ('34172001', 'Montpellier-Fréjorgues', 43.5761, 3.9631, 2, 34, 0, True, True),
    ('35238001', 'Rennes-Saint-Jacques', 48.0697, -1.7339, 36, 35, 0, True, True),
    ('21231001', 'Dijon-Longvic', 47.2681, 5.0900, 219, 21, 0, True, True),
    ('64445001', 'Pau-Uzein', 43.3803, -0.4186, 183, 64, 0, True, True),
]

def connect_db():
    """Connect to PostgreSQL database"""
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        print("✓ Connected to database")
        return conn
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        raise

def generate_stations(conn):
    """Insert station metadata"""
    cursor = conn.cursor()

    stations_data = []
    for station in STATIONS:
        station_id, name, lat, lon, alt, dept, type_poste, public, open_station = station
        stations_data.append((
            datetime.now(),  # createdAt
            datetime.now(),  # updatedAt
            station_id,
            name,
            dept,
            'horaire',  # frequence
            open_station,
            type_poste,
            lon,
            lat,
            alt,
            public
        ))

    insert_query = """
        INSERT INTO "Station"
        ("createdAt", "updatedAt", "id", "nom", "departement", "frequence",
         "posteOuvert", "typePoste", "lon", "lat", "alt", "postePublic")
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
    """

    execute_batch(cursor, insert_query, stations_data)
    conn.commit()
    print(f"✓ Inserted {len(stations_data)} stations")

def generate_temperature_profile(hour: int, base_temp: float, amplitude: float) -> float:
    """Generate realistic diurnal temperature variation"""
    # Temperature is lowest at 6am, highest at 3pm
    hour_rad = (hour - 6) * 2 * np.pi / 24
    return base_temp + amplitude * np.sin(hour_rad)

def generate_hourly_data(conn):
    """Generate hourly weather data for 1 month"""
    cursor = conn.cursor()

    # Generate data for last 30 days
    end_time = datetime.now().replace(minute=0, second=0, microsecond=0)
    start_time = end_time - timedelta(days=30)

    hourly_data = []

    for station in STATIONS:
        station_id, name, lat, lon, alt, dept, _, _, _ = station

        # Base climate parameters depending on location
        base_temp = 5 + (50 - lat) * 0.8 - alt * 0.006  # Warmer in south, cooler at altitude
        humidity_base = 70 + (lat - 45) * 2  # More humid in north

        current_time = start_time
        wind_direction = random.randint(0, 360)

        while current_time <= end_time:
            hour = current_time.hour

            # Temperature with diurnal cycle and random variation
            temp = generate_temperature_profile(hour, base_temp, 5) + random.gauss(0, 1.5)
            temp_dew = temp - random.uniform(2, 8)  # Dew point

            # Temperature extrema (reset daily)
            if hour == 0:
                daily_tx = temp
                daily_tn = temp
            else:
                daily_tx = max(daily_tx, temp) if 'daily_tx' in locals() else temp
                daily_tn = min(daily_tn, temp) if 'daily_tn' in locals() else temp

            # Humidity (inversely correlated with temperature)
            humidity = int(np.clip(humidity_base - (temp - base_temp) * 2 + random.gauss(0, 5), 30, 100))
            humidity_max = min(humidity + random.randint(5, 15), 100)
            humidity_min = max(humidity - random.randint(5, 15), 30)

            # Wind (direction changes slowly, speed with gusts)
            wind_direction += random.randint(-10, 10)
            wind_direction = wind_direction % 360
            wind_speed = abs(random.gauss(3, 2))  # m/s
            wind_gust = wind_speed + random.uniform(2, 8)
            wind_instant = wind_speed + random.uniform(-1, 3)

            # Precipitation (20% chance of rain)
            rain = random.uniform(0, 20) if random.random() < 0.2 else 0

            # Pressure (realistic range with slow variation)
            pressure_station = 1013 + random.gauss(0, 15)
            pressure_sea = pressure_station + alt * 0.12

            # Visibility (reduced in rain)
            visibility = int(10000 if rain < 1 else max(1000, 10000 - rain * 500))

            # Cloud cover (correlated with rain)
            clouds = int(np.clip(random.gauss(4, 3) + (rain > 0) * 3, 0, 8))

            # Solar radiation (depends on hour and clouds)
            if 6 <= hour <= 20:
                radiation = max(0, 800 * np.sin((hour - 6) * np.pi / 14) * (1 - clouds / 10) + random.gauss(0, 50))
            else:
                radiation = 0

            # Sunshine hours (depends on clouds)
            sunshine = max(0, 1 - clouds / 8) if 6 <= hour <= 20 else 0

            # Soil temperatures (lagged from air temperature)
            t_10 = temp - 2 + random.gauss(0, 0.5)
            t_20 = temp - 3 + random.gauss(0, 0.5)
            t_50 = temp - 4 + random.gauss(0, 0.5)
            t_100 = temp - 5 + random.gauss(0, 0.5)

            hourly_data.append((
                station_id,
                lat,
                lon,
                current_time,  # reference_time
                current_time,  # insert_time
                current_time,  # validity_time
                round(temp, 1),
                round(temp_dew, 1),
                round(daily_tx, 1) if 'daily_tx' in locals() else None,
                round(daily_tn, 1) if 'daily_tn' in locals() else None,
                humidity,
                humidity_max,
                humidity_min,
                wind_direction,
                round(wind_speed, 1),
                wind_direction,
                round(wind_gust, 1),
                wind_direction,
                round(wind_instant, 1),
                round(rain, 1) if rain > 0 else 0,
                round(t_10, 1),
                round(t_20, 1),
                round(t_50, 1),
                round(t_100, 1),
                visibility,
                0,  # etat_sol
                None,  # sss (snow)
                clouds,
                round(sunshine, 2),
                round(radiation, 0) if radiation > 0 else None,
                round(pressure_station, 1),
                round(pressure_sea, 1)
            ))

            current_time += timedelta(hours=1)

    insert_query = """
        INSERT INTO "HoraireTempsReel"
        ("geo_id_insee", "lat", "lon", "reference_time", "insert_time", "validity_time",
         "t", "td", "tx", "tn", "u", "ux", "un", "dd", "ff", "dxy", "fxy", "dxi", "fxi",
         "rr1", "t_10", "t_20", "t_50", "t_100", "vv", "etat_sol", "sss", "n", "insolh",
         "ray_glo01", "pres", "pmer")
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
    """

    # Insert in batches for performance
    batch_size = 1000
    for i in range(0, len(hourly_data), batch_size):
        batch = hourly_data[i:i + batch_size]
        execute_batch(cursor, insert_query, batch)
        conn.commit()
        print(f"✓ Inserted hourly batch {i//batch_size + 1}/{(len(hourly_data) + batch_size - 1)//batch_size}")

    print(f"✓ Inserted {len(hourly_data)} hourly records")

def generate_daily_data(conn):
    """Generate daily aggregated data from hourly data"""
    cursor = conn.cursor()

    # Aggregate from HoraireTempsReel
    aggregate_query = """
        INSERT INTO "Quotidienne"
        ("NUM_POSTE", "NOM_USUEL", "LAT", "LON", "ALTI", "AAAAMMJJ",
         "RR", "QRR", "TN", "QTN", "HTN", "QHTN", "TX", "QTX", "HTX", "QHTX",
         "TM", "QTM", "TNTXM", "QTNTXM", "TAMPLI", "QTAMPLI",
         "FFM", "QFFM", "FXY", "QFXY", "DXY", "QDXY", "HXY", "QHXY")
        SELECT
            h.geo_id_insee as "NUM_POSTE",
            s.nom as "NOM_USUEL",
            h.lat as "LAT",
            h.lon as "LON",
            s.alt as "ALTI",
            DATE_TRUNC('day', h.validity_time) as "AAAAMMJJ",
            ROUND(SUM(COALESCE(h.rr1, 0))::numeric, 1) as "RR",
            1 as "QRR",
            ROUND(MIN(h.t)::numeric, 1) as "TN",
            1 as "QTN",
            TO_CHAR((ARRAY_AGG(h.validity_time ORDER BY h.t ASC))[1], 'HH24MI') as "HTN",
            1 as "QHTN",
            ROUND(MAX(h.t)::numeric, 1) as "TX",
            1 as "QTX",
            TO_CHAR((ARRAY_AGG(h.validity_time ORDER BY h.t DESC))[1], 'HH24MI') as "HTX",
            1 as "QHTX",
            ROUND(AVG(h.t)::numeric, 1) as "TM",
            1 as "QTM",
            ROUND(((MIN(h.t) + MAX(h.t)) / 2)::numeric, 1) as "TNTXM",
            1 as "QTNTXM",
            ROUND((MAX(h.t) - MIN(h.t))::numeric, 1) as "TAMPLI",
            1 as "QTAMPLI",
            ROUND(AVG(h.ff)::numeric, 1) as "FFM",
            1 as "QFFM",
            ROUND(MAX(h.fxy)::numeric, 1) as "FXY",
            1 as "QFXY",
            (ARRAY_AGG(h.dxy ORDER BY h.fxy DESC))[1] as "DXY",
            1 as "QDXY",
            TO_CHAR((ARRAY_AGG(h.validity_time ORDER BY h.fxy DESC))[1], 'HH24MI') as "HXY",
            1 as "QHXY"
        FROM "HoraireTempsReel" h
        JOIN "Station" s ON h.geo_id_insee = s.id
        WHERE s.frequence = 'horaire'
        GROUP BY h.geo_id_insee, s.nom, h.lat, h.lon, s.alt, DATE_TRUNC('day', h.validity_time)
        ON CONFLICT DO NOTHING
    """

    cursor.execute(aggregate_query)
    conn.commit()
    rows_inserted = cursor.rowcount
    print(f"✓ Inserted {rows_inserted} daily records")

def display_summary(conn):
    """Display summary statistics"""
    cursor = conn.cursor()

    # Count stations
    cursor.execute('SELECT COUNT(*) FROM "Station"')
    station_count = cursor.fetchone()[0]

    # Count hourly records
    cursor.execute('SELECT COUNT(*) FROM "HoraireTempsReel"')
    hourly_count = cursor.fetchone()[0]

    # Count daily records
    cursor.execute('SELECT COUNT(*) FROM "Quotidienne"')
    daily_count = cursor.fetchone()[0]

    # Time range
    cursor.execute('SELECT MIN(validity_time), MAX(validity_time) FROM "HoraireTempsReel"')
    time_range = cursor.fetchone()

    # Check hypertables
    cursor.execute("""
        SELECT hypertable_name, num_chunks
        FROM timescaledb_information.hypertables
    """)
    hypertables = cursor.fetchall()

    print("\n" + "="*60)
    print("📊 MOCK DATA GENERATION SUMMARY")
    print("="*60)
    print(f"Stations created:       {station_count}")
    print(f"Hourly records:         {hourly_count}")
    print(f"Daily records:          {daily_count}")
    print(f"Time range:             {time_range[0]} to {time_range[1]}")
    print(f"\nTimescaleDB Hypertables:")
    for ht_name, chunks in hypertables:
        print(f"  - {ht_name}: {chunks} chunks")
    print("="*60)
    print("✓ Mock data generation complete!")
    print("\nNext steps:")
    print("  1. Connect to database: docker exec -it infoclimat-timescaledb psql -U infoclimat -d meteodb")
    print("  2. Query data: SELECT * FROM \"Station\" LIMIT 10;")
    print("="*60 + "\n")

def main():
    """Main execution"""
    print("\n🚀 Starting mock data generation for InfoClimat TimescaleDB\n")

    try:
        conn = connect_db()

        print("\n📍 Generating stations...")
        generate_stations(conn)

        print("\n⏰ Generating hourly data (this may take a minute)...")
        generate_hourly_data(conn)

        print("\n📅 Generating daily aggregated data...")
        generate_daily_data(conn)

        print("\n📈 Displaying summary...")
        display_summary(conn)

        conn.close()

    except Exception as e:
        print(f"\n✗ Error: {e}")
        raise

if __name__ == "__main__":
    main()
