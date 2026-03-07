from __future__ import annotations

from typing import Protocol

from .types import RecordPoint, RecordsQuery

class RecordsDataSource(Protocol):
    """
    Interface "source de données journalières" pour le calcul ITN.

    - En fake : génère une série journalière avec une climatologie.
    - En réel : requête DB (Timescale/Postgres) pour récupérer les points journaliers.
    """

    def fetch_daily_series(
        self,
        query: RecordsQuery,
    ) -> list[RecordPoint]: ...
