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
    annee_de_creation: int = 2000,
    classe_recente: int = 1,
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
        cur.execute(
            """
            INSERT INTO public."station_creation_date"
                ("station_code", "annee_de_creation")
            VALUES (%(code)s, %(annee)s)
            ON CONFLICT ("station_code") DO NOTHING
            """,
            {"code": code, "annee": annee_de_creation},
        )
        cur.execute(
            """
            INSERT INTO public."station_classe"
                ("station_code", "classe", "date_debut", "date_fin")
            VALUES (%(code)s, %(classe)s, '2000-01-01', NULL)
            ON CONFLICT ("station_code", "date_debut") DO NOTHING
            """,
            {"code": code, "classe": classe_recente},
        )
