import datetime as dt

from django.db import connection


def insert_quotidienne(
    day: dt.date,
    code: str,
    tntxm: float | None = None,
    *,
    tx: float | None = None,
    tn: float | None = None,
) -> None:
    if tntxm is None and tx is not None and tn is not None:
        tntxm = (tx + tn) / 2

    with connection.cursor() as cur:
        cur.execute(
            """
            INSERT INTO public."Quotidienne"
                ("NUM_POSTE", "NOM_USUEL", "LAT", "LON", "ALTI",
                 "AAAAMMJJ", "TX", "TN", "TNTXM")
            VALUES
                (%(code)s, %(name)s, 0, 0, 0,
                 %(day)s, %(tx)s, %(tn)s, %(tntxm)s)
            ON CONFLICT ("NUM_POSTE", "AAAAMMJJ")
            DO UPDATE SET
                "TX" = EXCLUDED."TX",
                "TN" = EXCLUDED."TN",
                "TNTXM" = EXCLUDED."TNTXM"
            """,
            {
                "code": code,
                "name": f"ST {code}",
                "day": day,
                "tx": tx,
                "tn": tn,
                "tntxm": tntxm,
            },
        )
