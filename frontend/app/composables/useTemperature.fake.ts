/**
 * Fake implementations of temperature composables for frontend development.
 * These return static data filtered client-side, without hitting the backend.
 */

import type {
    TemperatureRecordsParams,
    TemperatureRecordsResponse,
    TemperatureRecordEntry,
} from "~/types/api";

const fakeRecords = [
    {
        id: "07149",
        name: "Orly",
        departement: "94",
        TNN: -7.2,
        TXX: 32.1,
        TNN_date: "1980-01-15",
        TXX_date: "1980-07-18",
    },
    {
        id: "07156",
        name: "Paris-Montsouris",
        departement: "75",
        TNN: -11.4,
        TXX: 36.1,
        TNN_date: "1981-02-07",
        TXX_date: "1981-08-02",
    },
    {
        id: "07181",
        name: "Melun",
        departement: "77",
        TNN: -16.0,
        TXX: 38.0,
        TNN_date: "1982-01-19",
        TXX_date: "1982-07-23",
    },
    {
        id: "07222",
        name: "Tours",
        departement: "37",
        TNN: -14.3,
        TXX: 39.2,
        TNN_date: "1983-02-03",
        TXX_date: "1983-08-09",
    },
    {
        id: "07460",
        name: "Marseille-Marignane",
        departement: "13",
        TNN: -10.6,
        TXX: 41.0,
        TNN_date: "1985-01-08",
        TXX_date: "1985-07-30",
    },
    {
        id: "07510",
        name: "Bordeaux-Mérignac",
        departement: "33",
        TNN: -11.6,
        TXX: 41.2,
        TNN_date: "1987-02-12",
        TXX_date: "1987-08-14",
    },
    {
        id: "07130",
        name: "Lille-Lesquin",
        departement: "59",
        TNN: -15.5,
        TXX: 36.4,
        TNN_date: "1989-01-22",
        TXX_date: "1989-07-27",
    },
    {
        id: "07480",
        name: "Lyon-Bron",
        departement: "69",
        TNN: -18.8,
        TXX: 40.5,
        TNN_date: "1991-01-11",
        TXX_date: "1991-08-05",
    },
    {
        id: "07690",
        name: "Toulouse-Blagnac",
        departement: "31",
        TNN: -12.6,
        TXX: 40.9,
        TNN_date: "1992-02-17",
        TXX_date: "1992-07-21",
    },
    {
        id: "07371",
        name: "Strasbourg-Entzheim",
        departement: "67",
        TNN: -23.6,
        TXX: 38.9,
        TNN_date: "1994-01-28",
        TXX_date: "1994-08-01",
    },
    {
        id: "07230",
        name: "Clermont-Ferrand",
        departement: "63",
        TNN: -17.2,
        TXX: 39.8,
        TNN_date: "1995-02-04",
        TXX_date: "1995-07-25",
    },
    {
        id: "07434",
        name: "Montpellier",
        departement: "34",
        TNN: -9.4,
        TXX: 42.1,
        TNN_date: "1997-01-31",
        TXX_date: "1997-08-12",
    },
    {
        id: "07110",
        name: "Cherbourg",
        departement: "50",
        TNN: -8.1,
        TXX: 33.6,
        TNN_date: "1998-02-09",
        TXX_date: "1998-07-19",
    },
    {
        id: "07335",
        name: "Dijon",
        departement: "21",
        TNN: -19.5,
        TXX: 39.4,
        TNN_date: "1999-01-14",
        TXX_date: "1999-08-07",
    },
    {
        id: "07190",
        name: "Reims",
        departement: "51",
        TNN: -20.1,
        TXX: 38.3,
        TNN_date: "2000-02-21",
        TXX_date: "2000-07-31",
    },
    {
        id: "07255",
        name: "Bourges",
        departement: "18",
        TNN: -16.8,
        TXX: 40.1,
        TNN_date: "2002-01-06",
        TXX_date: "2002-08-03",
    },
    {
        id: "07540",
        name: "Agen",
        departement: "47",
        TNN: -10.3,
        TXX: 41.8,
        TNN_date: "2003-02-14",
        TXX_date: "2003-07-28",
    },
    {
        id: "07699",
        name: "Perpignan",
        departement: "66",
        TNN: -8.7,
        TXX: 43.2,
        TNN_date: "2005-01-18",
        TXX_date: "2005-08-16",
    },
    {
        id: "07270",
        name: "Nancy",
        departement: "54",
        TNN: -21.3,
        TXX: 37.8,
        TNN_date: "2006-02-25",
        TXX_date: "2006-07-22",
    },
    {
        id: "07461",
        name: "Nîmes",
        departement: "30",
        TNN: -9.1,
        TXX: 42.6,
        TNN_date: "2008-01-10",
        TXX_date: "2008-08-10",
    },
    {
        id: "07145",
        name: "Chartres",
        departement: "28",
        TNN: -18.4,
        TXX: 38.7,
        TNN_date: "2010-02-01",
        TXX_date: "2010-07-15",
    },
    {
        id: "07620",
        name: "Pau",
        departement: "64",
        TNN: -10.9,
        TXX: 40.3,
        TNN_date: "2012-01-24",
        TXX_date: "2012-08-19",
    },
    {
        id: "07280",
        name: "Metz",
        departement: "57",
        TNN: -22.4,
        TXX: 37.1,
        TNN_date: "2013-02-08",
        TXX_date: "2013-07-09",
    },
    {
        id: "07560",
        name: "Biarritz",
        departement: "64",
        TNN: -6.3,
        TXX: 39.0,
        TNN_date: "2015-01-17",
        TXX_date: "2015-08-23",
    },
    {
        id: "07207",
        name: "Rennes",
        departement: "35",
        TNN: -12.7,
        TXX: 38.2,
        TNN_date: "2017-02-11",
        TXX_date: "2017-07-04",
    },
    {
        id: "07120",
        name: "Rouen",
        departement: "76",
        TNN: -14.9,
        TXX: 37.6,
        TNN_date: "2019-01-29",
        TXX_date: "2019-07-25",
    },
    {
        id: "07650",
        name: "Millau",
        departement: "12",
        TNN: -15.6,
        TXX: 40.7,
        TNN_date: "2020-02-18",
        TXX_date: "2020-08-06",
    },
    {
        id: "07384",
        name: "Grenoble",
        departement: "38",
        TNN: -20.7,
        TXX: 39.5,
        TNN_date: "2022-01-05",
        TXX_date: "2022-07-17",
    },
    {
        id: "07747",
        name: "Toulon",
        departement: "83",
        TNN: -5.8,
        TXX: 40.8,
        TNN_date: "2024-02-22",
        TXX_date: "2024-08-01",
    },
    {
        id: "07790",
        name: "Nice",
        departement: "06",
        TNN: -4.2,
        TXX: 38.4,
        TNN_date: "2025-01-13",
        TXX_date: "2026-02-28",
    },
];

export function useTemperatureRecordsFake(
    params?: MaybeRef<TemperatureRecordsParams>,
) {
    const data = ref<TemperatureRecordsResponse | null>(null);
    const pending = ref(false);
    const error = ref(null);

    function compute(p: TemperatureRecordsParams): TemperatureRecordsResponse {
        const typeRecords = p.type_records ?? "hot";
        const recordKind = p.record_kind ?? "absolute";
        const recordScope = p.record_scope ?? "all_time";
        const dateStart = p.date_start ?? null;
        const dateEnd = p.date_end ?? null;
        const stationIds = p.station_ids ?? [];
        const departments = p.departments ?? [];
        const tempMin = p.temperature_min ?? null;
        const tempMax = p.temperature_max ?? null;
        const limit = p.limit ?? 10;
        const offset = p.offset ?? 0;

        let stations = fakeRecords;

        if (stationIds.length)
            stations = stations.filter((s) => stationIds.includes(s.id));
        if (departments.length)
            stations = stations.filter((s) =>
                departments.includes(s.departement),
            );

        const filterRecord = (r: TemperatureRecordEntry): boolean => {
            if (dateStart && r.date < dateStart) return false;
            if (dateEnd && r.date > dateEnd) return false;
            if (tempMin !== null && r.value < tempMin) return false;
            if (tempMax !== null && r.value > tempMax) return false;
            return true;
        };

        const mappedStations = stations.map((s) => ({
            id: s.id,
            name: s.name,
            departement: s.departement,
            hot_records:
                typeRecords !== "cold"
                    ? [{ value: s.TXX, date: s.TXX_date }].filter(filterRecord)
                    : [],
            cold_records:
                typeRecords !== "hot"
                    ? [{ value: s.TNN, date: s.TNN_date }].filter(filterRecord)
                    : [],
        }));

        const allStations = mappedStations.filter(
            (s) => s.hot_records.length > 0 || s.cold_records.length > 0,
        );

        // station_ids and departments are parallel arrays — index i of station_ids
        // corresponds to index i of departments, allowing callers to reconstruct
        // per-station department without a separate lookup.
        return {
            count: allStations.length,
            metadata: {
                date_start: dateStart,
                date_end: dateEnd,
                record_kind: recordKind,
                record_scope: recordScope,
                type_records: typeRecords,
                station_ids: allStations.map((s) => s.id),
                departments: allStations.map((s) => s.departement),
                temperature_min: tempMin,
                temperature_max: tempMax,
            },
            stations: allStations.slice(offset, offset + limit),
        };
    }

    let debounceTimer: ReturnType<typeof setTimeout> | null = null;

    watch(
        () => (isRef(params) ? params.value : (params ?? {})),
        (p) => {
            if (debounceTimer) clearTimeout(debounceTimer);
            pending.value = true;
            debounceTimer = setTimeout(() => {
                data.value = compute(p);
                pending.value = false;
            }, 600);
        },
        { immediate: true, deep: true },
    );

    return { data, pending, error };
}
