import datetime
import random
from dataclasses import dataclass

from weather.data_sources.national_indicator_fake import _climatology_for_date
from weather.services.records.types import (
    RecordPointSet,
    RecordsQuery,
    RecordValue,
)
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
    def __init__(self, *, seed: int = 420) -> None:
        self._seed = seed

    def fetch_records(self, query: RecordsQuery) -> list[RecordPointSet]:
        Stations = [
            _FakeStationInfo("01", "Station01"),
            _FakeStationInfo("02", "Station02"),
            _FakeStationInfo("03", "Station03"),
        ]

        RetList = []
        for p in Stations:
            stationrecords = self.generate_station_fake_record(query)

            RetList.append(self.extract_fake_records(p, stationrecords, query))

        return RetList

    def extract_fake_records(
        self,
        station: _FakeStationInfo,
        datapoints: list[_FakeTemperaturePoint],
        query: RecordsQuery,
    ) -> RecordPointSet:
        current_min = None
        current_max = None
        records_froid = []
        records_chaud = []

        print("datapoints", len(datapoints))
        for point in datapoints:
            if current_min is None or current_min > point.t:
                current_min = point.t
                print(station, current_min, "-", point.d)
                if point.d >= query.date_start and point.d <= query.date_end:
                    records_froid.append(RecordValue(current_min, point.d))
            if current_max is None or current_max < point.t:
                current_max = point.t
                print(station, "_", current_max, point.d)
                if point.d >= query.date_start and point.d <= query.date_end:
                    records_chaud.append(RecordValue(current_max, point.d))

        print(station.id, records_chaud, records_froid)
        return RecordPointSet(station.id, station.nom, records_chaud, records_froid)

    ## Random sequence of temperatures from day_start to enddate
    def generate_station_fake_record(self, query) -> list[_FakeTemperaturePoint]:
        rng = random.Random(self._seed)
        days = tuple(iter_days_intersecting(datetime.date(2000, 1, 1), query.date_end))
        ret = []
        index = 0
        for d in days:
            _, sigma, baseline_min, baseline_max = _climatology_for_date(d)
            ret.append(
                _FakeTemperaturePoint(
                    d, baseline_min + 1.25 * index / len(days) + rng.gauss(0.0, sigma)
                )
            )
            ret.append(
                _FakeTemperaturePoint(
                    d, baseline_max + 1.25 * index / len(days) + rng.gauss(0.0, sigma)
                )
            )
            index = index + 1

        return ret
