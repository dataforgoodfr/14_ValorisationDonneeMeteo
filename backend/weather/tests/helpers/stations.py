import datetime as dt

from django.db import connection


def insert_station(
    code: str,
    name: str = "Station test",
    *,
    departement: int = 1,
    lat: float = 0.0,
    lon: float = 0.0,
    alt: float = 0.0,
) -> None:
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
                 %(departement)s, 'horaire',
                 '1', 1,
                 %(lon)s, %(lat)s, %(alt)s, '1')
            """,
            {
                "created": now,
                "updated": now,
                "id": code,
                "name": name,
                "departement": departement,
                "lat": lat,
                "lon": lon,
                "alt": alt,
            },
        )
