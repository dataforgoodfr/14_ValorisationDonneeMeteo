import datetime
import random
from dataclasses import dataclass

from weather.data_sources.national_indicator_fake import _climatology_for_date
from weather.services.records.types import RecordPoint, RecordsQuery
from weather.utils.date_range import iter_days_intersecting


@dataclass
class FakeTemperaturePoint:
    d: datetime
    t: float


@dataclass
class FakeStationInfo:
    id: str
    nom: str


class FakeRecordsDataSource:
    def __init__(self, *, seed: int = 42) -> None:
        self._seed = seed

    def fetch_records(self, query: RecordsQuery) -> list[RecordPoint]:
        Stations = [
            FakeStationInfo("01", "Station01"),
            FakeStationInfo("02", "Station02"),
            FakeStationInfo("03", "Station03"),
        ]

        RetList = []
        for p in Stations:
            datapoints = self.generate_station_fake_record(query)
            RetList.append(self.ExtractFakeRecords(p, datapoints))

        return RetList

    def ExtractFakeRecords(
        self, station: FakeStationInfo, datapoints: list[FakeTemperaturePoint]
    ) -> RecordPoint:
        Min = None
        Max = None
        DateMin = None
        DateMax = None
        for point in datapoints:
            if Min is None or Min > point[2]:
                Min = point[2]
                DateMin = point[1]
            if Max is None or Max < point[2]:
                Max = point[2]
                DateMax = point[1]

        return RecordPoint(station.code, station.nom, Min, Max, DateMin, DateMax)

    ## Random sequence of temperatures from day_start to enddate
    def generate_station_fake_record(self, query) -> list[FakeTemperaturePoint]:
        rng = random.Random(self._seed)
        days = tuple(iter_days_intersecting(query.date_start, query.date_end))
        ret = []
        for d in days:
            baseline_mean, sigma, _, _ = _climatology_for_date(d)
            ret.append(FakeTemperaturePoint(d, baseline_mean + rng.gauss(0.0, sigma)))

        return ret
