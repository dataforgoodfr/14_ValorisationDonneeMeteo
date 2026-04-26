import pathlib

import pytest
from django.db import connection

BASE_DIR = pathlib.Path(__file__).resolve().parents[2]


@pytest.fixture(scope="session", autouse=True)
def setup_db_schema_and_views(django_db_setup, django_db_blocker):
    """
    Initialise la DB de test avec les tables + vues + MV nécessaires.
    """
    schema_sql = (BASE_DIR / "sql" / "schemas" / "001_source_tables.sql").read_text()
    ref_department_region_sql = (
        BASE_DIR / "sql" / "tables" / "001_table_ref_department_region.sql"
    ).read_text()
    v_station_sql = (BASE_DIR / "sql" / "views" / "001_v_station.sql").read_text()
    mv_quot_sql = (
        BASE_DIR / "sql" / "materialized_views" / "001_mv_quotidienne_realtime.sql"
    ).read_text()
    v_quot_sql = (BASE_DIR / "sql" / "views" / "002_v_quotidienne.sql").read_text()
    baseline_station_table_sql = (
        BASE_DIR / "sql" / "test_tables" / "baseline_station_daily_mean_9120.sql"
    ).read_text()
    itn_baseline_tables_sql = (
        BASE_DIR / "sql" / "test_tables" / "itn_baseline.sql"
    ).read_text()
    mv_itn_daily_sql = (
        BASE_DIR
        / "sql"
        / "materialized_views"
        / "itn"
        / "006_mv_itn_daily_observed.sql"
    ).read_text()

    with django_db_blocker.unblock():
        with connection.cursor() as cur:
            # Extension
            cur.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")

            # Nettoyage robuste
            cur.execute("DROP TABLE IF EXISTS public.mv_records_battus_meta;")
            cur.execute(
                "DROP MATERIALIZED VIEW IF EXISTS public.mv_records_battus CASCADE;"
            )
            cur.execute(
                "DROP MATERIALIZED VIEW IF EXISTS public.mv_itn_daily_observed CASCADE;"
            )
            cur.execute("DROP VIEW IF EXISTS public.v_quotidienne_itn CASCADE;")
            cur.execute("DROP VIEW IF EXISTS public.v_station CASCADE;")
            cur.execute(
                "DROP TABLE IF EXISTS public.baseline_station_daily_mean_1991_2020 CASCADE;"
            )

            # Schema
            cur.execute(schema_sql)
            cur.execute(ref_department_region_sql)

            # Views
            cur.execute(v_station_sql)

            # MV realtime
            cur.execute(mv_quot_sql)

            # Vue quotidienne
            cur.execute(v_quot_sql)

            # Tables de test
            cur.execute(baseline_station_table_sql)
            cur.execute(itn_baseline_tables_sql)

            # ✅ VRAIE MV ITN (plus de table fake)
            cur.execute(mv_itn_daily_sql)

            # Tables records (fake)
            cur.execute(
                "CREATE TABLE public.mv_records_battus_meta (cutoff_date DATE NOT NULL);"
            )
            cur.execute("""
                CREATE TABLE public.mv_records_battus (
                    period_type   text,
                    period_value  text,
                    record_type   text,
                    station_code  char(8),
                    station_name  text,
                    department    integer,
                    record_value  double precision,
                    record_date   timestamp
                );
            """)
