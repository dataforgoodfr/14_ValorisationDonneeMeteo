import type {
    TemperatureRecordsParams,
    TemperatureRecordsResponse,
} from "~/types/api";

const fakeResponse: TemperatureRecordsResponse = {
    metadata: {
        date_start: null,
        date_end: null,
        record_kind: "absolute",
        record_scope: "all_time",
        type_records: "all",
        station_ids: [],
        departments: [],
        temperature_min: null,
        temperature_max: null,
    },
    stations: [
        {
            id: "FR-metro",
            name: "France Métropolitaine",
            hot_records: [
                { value: 45.3, date: "2023-07-17" },
                { value: 44.1, date: "2023-07-24" },
                { value: 43.7, date: "2003-08-06" },
                { value: 43.4, date: "2019-06-28" },
                { value: 43.3, date: "2003-08-01" },
                { value: 42.9, date: "2019-06-28" },
                { value: 42.4, date: "2019-06-28" },
                { value: 42.1, date: "2003-08-12" },
                { value: 41.9, date: "2019-06-28" },
                { value: 41.9, date: "1983-07-05" },
                { value: 41.9, date: "2019-07-25" },
                { value: 41.8, date: "2023-07-24" },
                { value: 41.7, date: "2003-08-11" },
                { value: 41.7, date: "2019-07-25" },
                { value: 41.2, date: "2003-08-09" },
                { value: 41.0, date: "2003-08-01" },
                { value: 40.8, date: "2003-08-12" },
                { value: 40.6, date: "2019-07-24" },
                { value: 40.5, date: "2019-06-28" },
                { value: 40.5, date: "2019-07-24" },
                { value: 40.4, date: "2019-07-25" },
                { value: 40.3, date: "2019-06-27" },
                { value: 40.1, date: "2019-07-25" },
                { value: 39.8, date: "2019-07-25" },
                { value: 39.7, date: "2019-07-25" },
                { value: 39.5, date: "2019-07-25" },
                { value: 38.5, date: "1956-02-11" },
                { value: 38.0, date: "2019-07-25" },
                { value: 37.2, date: "2023-07-24" },
                { value: 35.3, date: "2019-06-27" },
            ],
            cold_records: [
                { value: -23.6, date: "2019-07-25" },
                { value: -22.4, date: "2019-07-25" },
                { value: -21.3, date: "2003-08-01" },
                { value: -20.7, date: "1956-02-10" },
                { value: -20.1, date: "1956-02-11" },
                { value: -19.5, date: "1956-02-10" },
                { value: -18.8, date: "2003-08-09" },
                { value: -18.4, date: "1956-02-11" },
                { value: -17.2, date: "1956-02-11" },
                { value: -16.8, date: "1956-02-10" },
                { value: -16.0, date: "1956-01-19" },
                { value: -15.6, date: "1983-07-05" },
                { value: -15.5, date: "1956-02-18" },
                { value: -14.9, date: "1956-02-11" },
                { value: -14.3, date: "1985-02-03" },
                { value: -13.8, date: "1956-02-03" },
                { value: -12.7, date: "1956-02-12" },
                { value: -12.6, date: "1956-02-03" },
                { value: -11.6, date: "1956-02-02" },
                { value: -11.4, date: "2023-07-24" },
                { value: -10.9, date: "1956-02-03" },
                { value: -10.6, date: "1956-01-08" },
                { value: -10.3, date: "1956-02-04" },
                { value: -9.4, date: "1956-02-04" },
                { value: -8.7, date: "1956-02-02" },
                { value: -8.1, date: "1956-02-18" },
                { value: -7.2, date: "1980-01-15" },
                { value: -6.3, date: "1956-02-03" },
                { value: -5.8, date: "1956-01-09" },
                { value: -4.2, date: "1956-02-11" },
                { value: -3.5, date: "1971-02-01" },
            ],
        },
    ],
};

export function useTemperatureRecordsChartFake(
    params?: MaybeRef<TemperatureRecordsParams>,
) {
    const data = computed((): TemperatureRecordsResponse => {
        const p = isRef(params) ? params.value : (params ?? {});
        const date_start = p.date_start;
        const date_end = p.date_end;

        const stations = fakeResponse.stations
            .map((station) => ({
                ...station,
                hot_records: station.hot_records.filter(
                    (r) =>
                        (!date_start || r.date >= date_start) &&
                        (!date_end || r.date <= date_end),
                ),
                cold_records: station.cold_records.filter(
                    (r) =>
                        (!date_start || r.date >= date_start) &&
                        (!date_end || r.date <= date_end),
                ),
            }))
            .filter(
                (s) => s.hot_records.length > 0 || s.cold_records.length > 0,
            );

        return {
            metadata: {
                ...fakeResponse.metadata,
                date_start: date_start ?? null,
                date_end: date_end ?? null,
            },
            stations,
        };
    });

    return { data, pending: ref(false), error: ref(null) };
}
