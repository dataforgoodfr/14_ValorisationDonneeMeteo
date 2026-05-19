import datetime as dt
import pathlib

import pytest
from django.db import connection

BASE_DIR = pathlib.Path(__file__).resolve().parents[2]  # ajuste selon ton arbo


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
                "tntxm": (tx + tn) / 2 if tx is not None and tn is not None else None,
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
                (period_type,     period_value,     record_type,     station_code,     station_name,     department,     record_value,     record_date)
            VALUES
                (%(period_type)s, %(period_value)s, %(record_type)s, %(station_code)s, %(station_name)s, %(department)s, %(record_value)s, %(record_date)s)
            """,
            {
                "period_type": period_type,
                "period_value": period_value,
                "record_type": record_type,
                "station_code": station_code,
                "station_name": station_name,
                "department": department,
                "record_value": value,
                "record_date": date,
            },
        )


def set_cutoff(date: dt.date) -> None:
    with connection.cursor() as cur:
        cur.execute("TRUNCATE public.mv_records_battus_meta;")
        cur.execute(
            """
            INSERT INTO public.mv_records_battus_meta (cutoff_date)
            VALUES (%(cutoff_date)s);
            """,
            {"cutoff_date": date},
        )


def clear_mv() -> None:
    with connection.cursor() as cur:
        cur.execute("TRUNCATE public.mv_records_battus;")
        cur.execute("TRUNCATE public.mv_records_battus_meta;")


def get_drop_mv_or_table_sql(
    *,
    mv_or_table_name: str,
    schema: str = "public",
) -> str:
    # mv_or_table_name est une vraie vue matérialisée en prod/dev, mais ici
    # le conftest la recrée comme TABLE ordinaire pour pouvoir y insérer des
    # données de test. Son type dépend donc de ce que la session précédente a
    # laissé : DROP TABLE échoue sur une MV et DROP MATERIALIZED VIEW échoue
    # sur une table. Le DO $$ consulte pg_matviews / pg_tables pour choisir
    # la bonne commande avant d'exécuter.
    return f"""
        DO $$ BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_matviews
                WHERE schemaname = '{schema}' AND matviewname = '{mv_or_table_name}'
            ) THEN
                DROP MATERIALIZED VIEW {schema}.{mv_or_table_name};
            ELSIF EXISTS (
                SELECT 1 FROM pg_tables
                WHERE schemaname = '{schema}' AND tablename = '{mv_or_table_name}'
            ) THEN
                DROP TABLE {schema}.{mv_or_table_name};
            END IF;
        END $$;
    """


@pytest.fixture(scope="session", autouse=True)
def setup_db_schema_and_views(django_db_setup, django_db_blocker):
    """
    Crée les tables sources + views dans la DB de test.
    """
    schema_sql = (BASE_DIR / "sql" / "schemas" / "001_source_tables.sql").read_text()
    ref_department_region_sql = (
        BASE_DIR / "sql" / "tables" / "001_table_ref_department_region.sql"
    ).read_text()
    v_station_qualifiee_hexagone_sql = (
        BASE_DIR / "sql" / "views" / "200_001_v_station_qualifiee_hexagone.sql"
    ).read_text()
    v_quotidienne_realtime_sql = (
        BASE_DIR / "sql" / "materialized_views" / "300_001_v_quotidienne_realtime.sql"
    ).read_text()
    mv_quotidienne_realtime_sql = (
        BASE_DIR / "sql" / "materialized_views" / "301_001_mv_quotidienne_realtime.sql"
    ).read_text()
    v_quotidienne = (
        BASE_DIR / "sql" / "views" / "310_002_v_quotidienne.sql"
    ).read_text()
    v_station_classe_1234 = (
        BASE_DIR / "sql" / "views" / "210_003_v_station_classe_1234.sql"
    ).read_text()
    v_station_classe_123_sql = (
        BASE_DIR / "sql" / "views" / "220_004_v_station_classe_123.sql"
    ).read_text()
    v_station_deviation_sql = (
        BASE_DIR / "sql" / "views" / "500_005_v_station_deviation.sql"
    ).read_text()
    v_station_records_sql = (
        BASE_DIR / "sql" / "views" / "400_006_v_station_records.sql"
    ).read_text()
    v_quotidienne_deviation = (
        BASE_DIR / "sql" / "views" / "510_008_v_quotidienne_deviation.sql"
    ).read_text()
    baseline_station_table_sql = (
        BASE_DIR
        / "sql"
        / "test_tables"
        / "520_mv_baseline_station_daily_mean_1991_2020.sql"
    ).read_text()
    itn_baseline_tables_sql = (
        BASE_DIR
        / "sql"
        / "test_tables"
        / "640_004_v_itn_baseline_monthly_1991_2020.sql"
    ).read_text()
    v_itn_daily_all_years_with_feb29_sql = (
        BASE_DIR
        / "sql"
        / "materialized_views"
        / "itn"
        / "720_007_v_itn_daily_all_years_with_feb29.sql"
    ).read_text()
    v_itn_absolute_extremes_daily_sql = (
        BASE_DIR
        / "sql"
        / "materialized_views"
        / "itn"
        / "730_008_v_itn_absolute_extremes_daily.sql"
    ).read_text()
    v_itn_absolute_extremes_monthly_sql = (
        BASE_DIR
        / "sql"
        / "materialized_views"
        / "itn"
        / "740_009_v_itn_absolute_extremes_monthly.sql"
    ).read_text()
    v_itn_absolute_extremes_yearly_sql = (
        BASE_DIR
        / "sql"
        / "materialized_views"
        / "itn"
        / "750_010_v_itn_absolute_extremes_yearly.sql"
    ).read_text()
    v_records_absolus_par_saison_sql = (
        BASE_DIR
        / "sql"
        / "materialized_views"
        / "records"
        / "430_004_v_records_absolus_par_saison.sql"
    ).read_text()
    v_records_absolus_sql = (
        BASE_DIR
        / "sql"
        / "materialized_views"
        / "records"
        / "440_005_v_records_absolus.sql"
    ).read_text()
    v_records_absolus_par_type_sql = (
        BASE_DIR
        / "sql"
        / "materialized_views"
        / "records"
        / "450_006_v_records_absolus_par_type.sql"
    ).read_text()

    with django_db_blocker.unblock():
        with connection.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")
            cur.execute("DROP TABLE IF EXISTS public.mv_records_battus_meta;")
            cur.execute(get_drop_mv_or_table_sql(mv_or_table_name="mv_records_battus"))
            cur.execute(
                get_drop_mv_or_table_sql(mv_or_table_name="mv_first_temperature_date")
            )
            cur.execute("DROP VIEW IF EXISTS public.v_quotidienne CASCADE;")
            cur.execute(
                "DROP VIEW IF EXISTS public.v_station_qualifiee_hexagone CASCADE;"
            )
            cur.execute(
                "DROP TABLE IF EXISTS public.mv_baseline_station_daily_mean_1991_2020 CASCADE;"
            )
            cur.execute(schema_sql)
            cur.execute(ref_department_region_sql)
            cur.execute("""
                CREATE TABLE public.mv_first_temperature_date (
                    station_code           char(8),
                    first_temperature_date timestamp,
                    CONSTRAINT "mv_first_temperature_date_pkey" PRIMARY KEY ("station_code")
                );
            """)
            cur.execute(v_station_qualifiee_hexagone_sql)
            cur.execute(v_quotidienne_realtime_sql)
            cur.execute(mv_quotidienne_realtime_sql)
            cur.execute(v_quotidienne)
            cur.execute(v_station_classe_1234)
            cur.execute(v_station_classe_123_sql)
            cur.execute(v_station_deviation_sql)
            cur.execute(v_station_records_sql)
            cur.execute(v_quotidienne_deviation)
            cur.execute(baseline_station_table_sql)
            cur.execute(itn_baseline_tables_sql)
            cur.execute(
                get_drop_mv_or_table_sql(mv_or_table_name="mv_itn_daily_all_years_sql")
            )
            cur.execute("""
                DROP TABLE IF EXISTS public.mv_itn_daily_all_years;
                CREATE TABLE public.mv_itn_daily_all_years (
                    date         date             NOT NULL,
                    year         integer          NOT NULL,
                    month        integer          NOT NULL,
                    day_of_month integer          NOT NULL,
                    is_fictive   boolean          NOT NULL DEFAULT FALSE,
                    itn          double precision NOT NULL
                );
            """)
            cur.execute(v_itn_daily_all_years_with_feb29_sql)
            cur.execute(v_itn_absolute_extremes_daily_sql)
            cur.execute(v_itn_absolute_extremes_monthly_sql)
            cur.execute(v_itn_absolute_extremes_yearly_sql)
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
            cur.execute("""
                CREATE TABLE public.mv_records_absolus_par_mois (
                    station_code  char(8),
                    month         integer,
                    txx_max       double precision,
                    txx_max_date  timestamp,
                    tnn_min       double precision,
                    tnn_min_date  timestamp,
                    CONSTRAINT "mv_records_absolus_par_mois_pkey" PRIMARY KEY (station_code, month)
                );
            """)
            cur.execute(v_records_absolus_par_saison_sql)
            cur.execute(v_records_absolus_sql)
            cur.execute(v_records_absolus_par_type_sql)
