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
    annee_de_creation: int = 1950,
    classe_recente: int = 1,
    first_temperature_date: dt.date = dt.date(1950, 1, 1),
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
            ON CONFLICT ("id", "frequence") DO UPDATE SET
                "updatedAt" = EXCLUDED."updatedAt",
                "nom" = EXCLUDED."nom",
                "departement" = EXCLUDED."departement",
                "lon" = EXCLUDED."lon",
                "lat" = EXCLUDED."lat",
                "alt" = EXCLUDED."alt"
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
                   ("station_code", "date_de_creation")
            VALUES (%(code)s,       %(date_de_creation)s)
            ON CONFLICT ("station_code") DO NOTHING
            """,
            {
                "code": code,
                "date_de_creation": dt.date(annee_de_creation, 1, 1),
            },
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
        cur.execute(
            """
            INSERT INTO public."mv_first_temperature_date"
                ("station_code", "first_temperature_date")
            VALUES (%(code)s, %(first_temperature_date)s)
            ON CONFLICT ("station_code") DO UPDATE SET "first_temperature_date" = EXCLUDED."first_temperature_date"
            """,
            {"code": code, "first_temperature_date": first_temperature_date},
        )
