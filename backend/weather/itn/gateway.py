from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol

import pandas as pd


class ReadTemperaturesGateway(Protocol):
    """
    Interface pour la lecture des températures journalières
    nécessaires au calcul de l'ITN.
    """

    def __call__(
        self,
        stations_itn: Iterable | None = None,
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Parameters
        ----------
        stations_itn
              liste des codes stations à considérer.

        Returns
        -------
        stations: pd.DataFrame
              DataFrame avec colonnes : id, code, nom
        temp_daily: pd.DataFrame
              DataFrame avec colonnes : station_id, nom, date, temp_max, temp_min, tntxm
        """
        ...
