import datetime as dt

from django.db import connection


def insert_station(code: str, name: str = "Station test") -> None:
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
                 1, 'horaire',
                 '1', 1,
                 0.0, 0.0, 0.0, '1')
            """,
            {
                "created": now,
                "updated": now,
                "id": code,
                "name": name,
            },
        )
