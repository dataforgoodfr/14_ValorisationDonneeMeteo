import pathlib

import pytest
from django.db import connection

BASE_DIR = pathlib.Path(__file__).resolve().parents[2]  # ajuste selon ton arbo


@pytest.fixture(scope="session", autouse=True)
def setup_db_schema_and_views(django_db_setup, django_db_blocker):
    """
    Crée les tables sources + views dans la DB de test.
    """
    schema_sql = (BASE_DIR / "sql" / "schemas" / "001_source_tables.sql").read_text()
    v_station_sql = (BASE_DIR / "sql" / "views" / "001_v_station.sql").read_text()
    v_quot_sql = (BASE_DIR / "sql" / "views" / "002_v_quotidienne.sql").read_text()
    v_records_sql = (BASE_DIR / "sql" / "views" / "003_v_records_absolus.sql").read_text()
    baseline_mv_sql = (
        BASE_DIR / "sql" / "materialized_views" / "baseline-station-daily-mean-9120.sql"
    ).read_text()
    itn_baseline_tables_sql = (
        BASE_DIR / "sql" / "test_tables" / "itn_baseline.sql"
    ).read_text()

    with django_db_blocker.unblock():
        with connection.cursor() as cur:
            # Drop dependent views/MV before recreating source tables (idempotent setup).
            # Use a DO block to handle both TABLE and MATERIALIZED VIEW cases,
            # since DROP MATERIALIZED VIEW fails if the object exists as a plain table.
            cur.execute("""
                DO $$ BEGIN
                    BEGIN
                        DROP MATERIALIZED VIEW IF EXISTS public.baseline_station_daily_mean_1991_2020 CASCADE;
                    EXCEPTION WHEN wrong_object_type THEN
                        DROP TABLE IF EXISTS public.baseline_station_daily_mean_1991_2020 CASCADE;
                    END;
                END $$;
            """)
            cur.execute("DROP TABLE IF EXISTS public.mv_records_absolus_meta;")
            cur.execute("DROP TABLE IF EXISTS public.mv_records_absolus;")
            cur.execute("DROP VIEW IF EXISTS public.v_records_absolus CASCADE;")
            cur.execute("DROP VIEW IF EXISTS public.v_quotidienne_itn CASCADE;")
            cur.execute("DROP VIEW IF EXISTS public.v_station CASCADE;")
            cur.execute(schema_sql)
            cur.execute(v_station_sql)
            cur.execute(v_quot_sql)
            cur.execute(v_records_sql)
            cur.execute(baseline_mv_sql)
            cur.execute(itn_baseline_tables_sql)
            cur.execute(
                "CREATE TABLE public.mv_records_absolus_meta (cutoff_date DATE NOT NULL);"
            )
            cur.execute("""
                CREATE TABLE public.mv_records_absolus (
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
