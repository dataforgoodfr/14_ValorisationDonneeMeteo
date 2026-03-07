from __future__ import annotations

from typing import Protocol

from .types import RecordPoint, RecordsQuery

class RecordsDataSource(Protocol):
    """
    Interface "Records" pour le services Records de température.

    - En fake : génère une série journalière avec une climatologie.
    - En réel : requête DB (Timescale/Postgres) pour récupérer les points journaliers.
    """

    def fetch_records(
        self,
        query: RecordsQuery,
    ) -> list[RecordPoint]: ...
