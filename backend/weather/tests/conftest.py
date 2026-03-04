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

    with django_db_blocker.unblock():
        with connection.cursor() as cur:
            cur.execute(schema_sql)
            cur.execute(v_station_sql)
            cur.execute(v_quot_sql)
