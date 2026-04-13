import datetime as dt
import pathlib

import pytest
from django.db import connection

BASE_DIR = pathlib.Path(__file__).resolve().parents[2]  # ajuste selon ton arbo


def insert_station(code: str, name: str = "Station test", department: int = 1) -> None:
    now = dt.datetime.now()
    with connection.cursor() as cur:
        cur.execute(
            """
            INSERT INTO public."Station"
                ("createdAt", "updatedAt", "id", "nom",
                 "departement", "frequence",
                 "posteOuvert", "typePoste",
                 "lon", "lat", "alt", "postePublic")
            VALUES
                (%(created)s, %(updated)s, %(id)s, %(name)s,
                 %(dept)s, 'horaire',
                 '1', 1,
                 0.0, 0.0, 0.0, '1')
            ON CONFLICT ("id", "frequence") DO UPDATE SET "nom" = EXCLUDED."nom"
            """,
            {
                "created": now,
                "updated": now,
                "id": code,
                "name": name,
                "dept": department,
            },
        )


def insert_quotidienne(
    day: dt.date,
    code: str,
    *,
    tx: float | None = None,
    tn: float | None = None,
) -> None:
    with connection.cursor() as cur:
        cur.execute(
            """
            INSERT INTO public."Quotidienne"
                ("NUM_POSTE", "NOM_USUEL", "LAT", "LON", "ALTI", "AAAAMMJJ", "TX", "TN", "TNTXM")
            VALUES
                (%(code)s, %(name)s, 0, 0, 0, %(day)s, %(tx)s, %(tn)s, %(tntxm)s)
            ON CONFLICT ("NUM_POSTE", "AAAAMMJJ")
            DO UPDATE SET "TX" = EXCLUDED."TX", "TN" = EXCLUDED."TN", "TNTXM" = EXCLUDED."TNTXM"
            """,
            {
                "code": code,
                "name": f"ST {code}",
                "day": day,
                "tx": tx,
                "tn": tn,
                "tntxm": ((tx or 0) + (tn or 0)) / 2 if tx and tn else None,
            },
        )


def insert_mv_record(
    station_code: str,
    station_name: str,
    period_type: str,
    period_value: str | None,
    record_type: str,
    value: float,
    date: dt.date,
    department: int = 75,
) -> None:
    with connection.cursor() as cur:
        cur.execute(
            """
            INSERT INTO public.mv_records_battus
                (period_type, period_value, record_type,
                 station_code, station_name, department,
                 record_value, record_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            [
                period_type,
                period_value,
                record_type,
                station_code,
                station_name,
                department,
                value,
                date,
            ],
        )


def set_cutoff(date: dt.date) -> None:
    with connection.cursor() as cur:
        cur.execute("TRUNCATE public.mv_records_battus_meta;")
        cur.execute(
            "INSERT INTO public.mv_records_battus_meta (cutoff_date) VALUES (%s);",
            [date],
        )


def clear_mv() -> None:
    with connection.cursor() as cur:
        cur.execute("TRUNCATE public.mv_records_battus;")
        cur.execute("TRUNCATE public.mv_records_battus_meta;")


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
    v_quot_sql = (BASE_DIR / "sql" / "views" / "002_v_quotidienne.sql").read_text()
    baseline_station_table_sql = (
        BASE_DIR / "sql" / "test_tables" / "baseline_station_daily_mean_9120.sql"
    ).read_text()
    itn_baseline_tables_sql = (
        BASE_DIR / "sql" / "test_tables" / "itn_baseline.sql"
    ).read_text()

    with django_db_blocker.unblock():
        with connection.cursor() as cur:
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
            cur.execute("DROP VIEW IF EXISTS public.v_quotidienne_itn CASCADE;")
            cur.execute("DROP VIEW IF EXISTS public.v_station CASCADE;")
            cur.execute(
                "DROP TABLE IF EXISTS public.baseline_station_daily_mean_1991_2020 CASCADE;"
            )
            cur.execute(schema_sql)
            cur.execute(ref_department_region_sql)
            cur.execute(v_station_sql)
            cur.execute(v_quot_sql)
            cur.execute(baseline_station_table_sql)
            cur.execute(itn_baseline_tables_sql)
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
