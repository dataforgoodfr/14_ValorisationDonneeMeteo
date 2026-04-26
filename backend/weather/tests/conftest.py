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
    itn_daily_observed_table_sql = (
        BASE_DIR / "sql" / "test_tables" / "mv_itn_daily_observed.sql"
    ).read_text()

    with django_db_blocker.unblock():
        with connection.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")
            cur.execute("DROP TABLE IF EXISTS public.mv_records_battus_meta;")
            # mv_records_battus est une vraie vue matérialisée en prod/dev, mais ici
            # le conftest la recrée comme TABLE ordinaire pour pouvoir y insérer des
            # données de test. Son type dépend donc de ce que la session précédente a
            # laissé : DROP TABLE échoue sur une MV et DROP MATERIALIZED VIEW échoue
            # sur une table. Le DO $$ consulte pg_matviews / pg_tables pour choisir
            # la bonne commande avant d'exécuter.
            cur.execute("""
                DO $$ BEGIN
                    IF EXISTS (
                        SELECT 1 FROM pg_matviews
                        WHERE schemaname = 'public' AND matviewname = 'mv_records_battus'
                    ) THEN
                        DROP MATERIALIZED VIEW public.mv_records_battus;
                    ELSIF EXISTS (
                        SELECT 1 FROM pg_tables
                        WHERE schemaname = 'public' AND tablename = 'mv_records_battus'
                    ) THEN
                        DROP TABLE public.mv_records_battus;
                    END IF;
                END $$;
            """)
            cur.execute("DROP TABLE IF EXISTS public.mv_itn_daily_observed CASCADE;")
            cur.execute("DROP VIEW IF EXISTS public.v_quotidienne_itn CASCADE;")
            cur.execute("DROP VIEW IF EXISTS public.v_station CASCADE;")
            cur.execute(
                "DROP TABLE IF EXISTS public.baseline_station_daily_mean_1991_2020 CASCADE;"
            )
            cur.execute(schema_sql)
            cur.execute(ref_department_region_sql)
            cur.execute(v_station_sql)
            cur.execute(mv_quot_sql)
            cur.execute(v_quot_sql)
            cur.execute(baseline_station_table_sql)
            cur.execute(itn_baseline_tables_sql)
            cur.execute(itn_daily_observed_table_sql)
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
