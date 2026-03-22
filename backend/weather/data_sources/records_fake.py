import datetime
import random
from dataclasses import dataclass

from weather.data_sources.national_indicator_fake import _climatology_for_date
from weather.services.records.types import RecordPoint, RecordsQuery
from weather.utils.date_range import iter_days_intersecting


@dataclass
class _FakeTemperaturePoint:
    d: datetime
    t: float


@dataclass
class _FakeStationInfo:
    id: str
    nom: str


class FakeRecordsDataSource:
    def __init__(self, *, seed: int = 42) -> None:
        self._seed = seed

    def fetch_records(self, query: RecordsQuery) -> list[RecordPoint]:
        Stations = [
            _FakeStationInfo("01", "Station01"),
            _FakeStationInfo("02", "Station02"),
            _FakeStationInfo("03", "Station03"),
        ]

        RetList = []
        for p in Stations:
            datapoints = self.generate_station_fake_record(query)
            RetList.append(self.extract_fake_records(p, datapoints))

        return RetList

    def extract_fake_records(
        self, station: _FakeStationInfo, datapoints: list[_FakeTemperaturePoint]
    ) -> RecordPoint:
        Min = None
        Max = None
        DateMin = None
        DateMax = None
        for point in datapoints:
            if Min is None or Min > point.t:
                Min = point.t
                DateMin = point.d
            if Max is None or Max < point.t:
                Max = point.t
                DateMax = point.d

        return RecordPoint(station.id, station.nom, Min, Max, DateMin, DateMax)

    ## Random sequence of temperatures from day_start to enddate
    def generate_station_fake_record(self, query) -> list[_FakeTemperaturePoint]:
        rng = random.Random(self._seed)
        days = tuple(iter_days_intersecting(query.date_start, query.date_end))
        ret = []
        for d in days:
            baseline_mean, sigma, _, _ = _climatology_for_date(d)
            ret.append(_FakeTemperaturePoint(d, baseline_mean + rng.gauss(0.0, sigma)))

        return ret
