"""
TimescaleDB hypertables migration.
Creates the TimescaleDB extension and converts time-series tables to hypertables.

TimescaleDB requires that any unique constraint (including primary keys) includes
the partitioning column. We handle this by:
1. Dropping the Django-generated primary key constraint
2. Creating the hypertable
3. Recreating a composite primary key that includes both id and the time column
"""

from django.db import migrations


class Migration(migrations.Migration):
    # TimescaleDB operations (CREATE EXTENSION, create_hypertable) cannot run
    # inside a transaction block. Disable atomic execution for this migration.
    atomic = False

    dependencies = [
        ("weather", "0001_initial"),
    ]

    operations = [
        # Create TimescaleDB extension
        migrations.RunSQL(
            sql="CREATE EXTENSION IF NOT EXISTS timescaledb;",
            reverse_sql="DROP EXTENSION IF EXISTS timescaledb;",
        ),
        # HoraireTempsReel: Drop PK, create hypertable, recreate composite PK
        migrations.RunSQL(
            sql="ALTER TABLE weather_horairetempsreel DROP CONSTRAINT weather_horairetempsreel_pkey;",
            reverse_sql="ALTER TABLE weather_horairetempsreel ADD PRIMARY KEY (id);",
        ),
        migrations.RunSQL(
            sql="""
                SELECT create_hypertable(
                    'weather_horairetempsreel',
                    'validity_time',
                    if_not_exists => TRUE,
                    chunk_time_interval => INTERVAL '7 days',
                    migrate_data => TRUE
                );
            """,
            reverse_sql="SELECT 1;",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE weather_horairetempsreel ADD PRIMARY KEY (id, validity_time);",
            reverse_sql="ALTER TABLE weather_horairetempsreel DROP CONSTRAINT weather_horairetempsreel_pkey;",
        ),
        # Quotidienne: Drop PK, create hypertable, recreate composite PK
        migrations.RunSQL(
            sql="ALTER TABLE weather_quotidienne DROP CONSTRAINT weather_quotidienne_pkey;",
            reverse_sql="ALTER TABLE weather_quotidienne ADD PRIMARY KEY (id);",
        ),
        migrations.RunSQL(
            sql="""
                SELECT create_hypertable(
                    'weather_quotidienne',
                    'date',
                    if_not_exists => TRUE,
                    chunk_time_interval => INTERVAL '30 days',
                    migrate_data => TRUE
                );
            """,
            reverse_sql="SELECT 1;",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE weather_quotidienne ADD PRIMARY KEY (id, date);",
            reverse_sql="ALTER TABLE weather_quotidienne DROP CONSTRAINT weather_quotidienne_pkey;",
        ),
        # Create composite indexes for efficient queries
        migrations.RunSQL(
            sql="CREATE INDEX IF NOT EXISTS idx_hourly_station_time ON weather_horairetempsreel (station_id, validity_time DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_hourly_station_time;",
        ),
        migrations.RunSQL(
            sql="CREATE INDEX IF NOT EXISTS idx_daily_station_date ON weather_quotidienne (station_id, date DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_daily_station_date;",
        ),
    ]
