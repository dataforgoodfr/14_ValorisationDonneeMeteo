from weather.services.national_indicator.protocols import (
    NationalIndicatorAbsoluteExtremesDataSource,
)
from weather.services.national_indicator.types import AbsoluteExtremes


class StubAbsoluteExtremes(NationalIndicatorAbsoluteExtremesDataSource):
    """Stub renvoyant des extremes fixes (-50.0 / 50.0) pour tous les tests."""

    def fetch_daily_absolute_extremes(
        self, month_day_pairs: set[tuple[int, int]]
    ) -> dict[tuple[int, int], AbsoluteExtremes]:
        return {
            k: AbsoluteExtremes(absolute_min=-50.0, absolute_max=50.0)
            for k in month_day_pairs
        }

    def fetch_monthly_absolute_extremes(
        self, months: set[int]
    ) -> dict[int, AbsoluteExtremes]:
        return {
            m: AbsoluteExtremes(absolute_min=-50.0, absolute_max=50.0) for m in months
        }

    def fetch_yearly_absolute_extremes(self) -> AbsoluteExtremes:
        return AbsoluteExtremes(absolute_min=-50.0, absolute_max=50.0)


stub_absolute_extremes = StubAbsoluteExtremes()
