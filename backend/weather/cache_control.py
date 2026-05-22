"""Mixin DRF émettant un en-tête `Cache-Control` selon un profil par vue.

Deux profils :
- ``"long"``        : TTL long systématique. Réservé aux endpoints dont la
                      fraîcheur est garantie par la purge par tag déclenchée
                      depuis le pipeline d'ingestion (stations, baselines,
                      records).
- ``"by_date_end"`` : discrimine via le paramètre ``date_end`` de la query
                      string. Si la plage est antérieure à ``today - N jours``,
                      TTL long ; sinon TTL court (la plage peut inclure J/J-1).

Aucune émission sur les réponses non-200 ni sur les méthodes autres que GET.
"""

from __future__ import annotations

import datetime as dt
import logging
from typing import Literal

logger = logging.getLogger(__name__)

CacheProfile = Literal["long", "by_date_end"]


class CacheControlMixin:
    """Ajoute `Cache-Control` aux réponses 200 d'une APIView / ViewSet DRF.

    Attributs de configuration par classe :
        cache_profile : profil de cache (voir module docstring) ou ``None`` pour
            désactiver complètement.
        cache_long_s_maxage / cache_long_max_age : TTL "long" (edge / browser).
        cache_short_s_maxage / cache_short_max_age : TTL "court".
        cache_date_end_threshold_days : seuil en jours entre "historique" (long)
            et "récent" (court). Garde une marge pour le délai d'ingestion.
        cache_date_end_query_param : nom du paramètre query string à lire.
    """

    cache_profile: CacheProfile | None = None
    cache_long_s_maxage: int = 86_400
    cache_long_max_age: int = 3_600
    cache_short_s_maxage: int = 900
    cache_short_max_age: int = 60
    cache_date_end_threshold_days: int = 2
    cache_date_end_query_param: str = "date_end"

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        if self.cache_profile is None:
            return response
        if request.method != "GET":
            return response
        if response.status_code != 200:
            return response
        s_maxage, max_age = self._compute_cache_ttls(request)
        response["Cache-Control"] = f"public, s-maxage={s_maxage}, max-age={max_age}"
        return response

    def _compute_cache_ttls(self, request) -> tuple[int, int]:
        if self.cache_profile == "long":
            return self.cache_long_s_maxage, self.cache_long_max_age
        if self.cache_profile == "by_date_end":
            return self._ttls_by_date_end(request)
        raise ValueError(f"Profil de cache inconnu : {self.cache_profile!r}")

    def _ttls_by_date_end(self, request) -> tuple[int, int]:
        raw = request.query_params.get(self.cache_date_end_query_param)
        if not raw:
            return self.cache_long_s_maxage, self.cache_long_max_age

        try:
            date_end = dt.date.fromisoformat(raw)
        except ValueError:
            # Une réponse 200 avec un date_end illisible ne devrait pas arriver
            # (le serializer rejette en 400), mais on reste défensif.
            logger.warning(
                "CacheControlMixin: date_end illisible (%r) — TTL court appliqué.",
                raw,
            )
            return self.cache_short_s_maxage, self.cache_short_max_age

        threshold = self._today() - dt.timedelta(
            days=self.cache_date_end_threshold_days
        )
        if date_end < threshold:
            return self.cache_long_s_maxage, self.cache_long_max_age
        return self.cache_short_s_maxage, self.cache_short_max_age

    def _today(self) -> dt.date:
        """Hook isolant `date.today()` pour faciliter le mock dans les tests."""
        return dt.date.today()
