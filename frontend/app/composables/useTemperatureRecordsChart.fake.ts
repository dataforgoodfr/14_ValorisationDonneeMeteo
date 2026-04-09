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
            id: "07149",
            name: "Orly",
            hot_records: [{ value: 42.1, date: "2003-08-12" }],
            cold_records: [{ value: -7.2, date: "1980-01-15" }],
        },
        {
            id: "07156",
            name: "Paris-Montsouris",
            hot_records: [{ value: 40.4, date: "2019-07-25" }],
            cold_records: [{ value: -11.4, date: "1956-02-10" }],
        },
        {
            id: "07181",
            name: "Melun",
            hot_records: [{ value: 38.0, date: "1976-07-19" }],
            cold_records: [{ value: -16.0, date: "1968-01-19" }],
        },
        {
            id: "07222",
            name: "Tours",
            hot_records: [{ value: 41.2, date: "2003-08-09" }],
            cold_records: [{ value: -14.3, date: "1985-02-03" }],
        },
        {
            id: "07460",
            name: "Marseille-Marignane",
            hot_records: [{ value: 44.1, date: "2023-07-24" }],
            cold_records: [{ value: -10.6, date: "1956-01-08" }],
        },
        {
            id: "07510",
            name: "Bordeaux-Mérignac",
            hot_records: [{ value: 42.4, date: "2019-06-28" }],
            cold_records: [{ value: -11.6, date: "1971-01-16" }],
        },
        {
            id: "07130",
            name: "Lille-Lesquin",
            hot_records: [{ value: 38.5, date: "2006-07-19" }],
            cold_records: [{ value: -15.5, date: "1987-01-13" }],
        },
        {
            id: "07480",
            name: "Lyon-Bron",
            hot_records: [{ value: 41.9, date: "2019-06-28" }],
            cold_records: [{ value: -18.8, date: "1963-02-10" }],
        },
        {
            id: "07690",
            name: "Toulouse-Blagnac",
            hot_records: [{ value: 43.3, date: "2003-08-01" }],
            cold_records: [{ value: -12.6, date: "1974-02-03" }],
        },
        {
            id: "07371",
            name: "Strasbourg",
            hot_records: [{ value: 39.7, date: "2015-07-05" }],
            cold_records: [{ value: -23.6, date: "1956-02-11" }],
        },
        {
            id: "07230",
            name: "Clermont-Ferrand",
            hot_records: [{ value: 40.8, date: "2003-08-12" }],
            cold_records: [{ value: -17.2, date: "1971-02-11" }],
        },
        {
            id: "07434",
            name: "Montpellier",
            hot_records: [{ value: 43.4, date: "2019-06-28" }],
            cold_records: [{ value: -9.4, date: "1991-02-04" }],
        },
        {
            id: "07110",
            name: "Cherbourg",
            hot_records: [{ value: 35.3, date: "2022-06-17" }],
            cold_records: [{ value: -8.1, date: "1963-02-18" }],
        },
        {
            id: "07335",
            name: "Dijon",
            hot_records: [{ value: 40.6, date: "2019-07-24" }],
            cold_records: [{ value: -19.5, date: "1956-02-10" }],
        },
        {
            id: "07190",
            name: "Reims",
            hot_records: [{ value: 41.9, date: "2010-08-07" }],
            cold_records: [{ value: -20.1, date: "1963-02-11" }],
        },
        {
            id: "07255",
            name: "Bourges",
            hot_records: [{ value: 41.7, date: "2003-08-11" }],
            cold_records: [{ value: -16.8, date: "1977-01-18" }],
        },
        {
            id: "07540",
            name: "Agen",
            hot_records: [{ value: 43.7, date: "1994-07-28" }],
            cold_records: [{ value: -10.3, date: "1956-02-04" }],
        },
        {
            id: "07699",
            name: "Perpignan",
            hot_records: [{ value: 45.3, date: "2023-07-17" }],
            cold_records: [{ value: -8.7, date: "1960-02-02" }],
        },
        {
            id: "07270",
            name: "Nancy",
            hot_records: [{ value: 39.8, date: "2019-07-25" }],
            cold_records: [{ value: -21.3, date: "1956-02-11" }],
        },
        {
            id: "07145",
            name: "Chartres",
            hot_records: [{ value: 40.1, date: "2019-07-25" }],
            cold_records: [{ value: -18.4, date: "1963-02-11" }],
        },
        {
            id: "07620",
            name: "Pau",
            hot_records: [{ value: 42.9, date: "2019-06-28" }],
            cold_records: [{ value: -10.9, date: "1985-02-03" }],
        },
        {
            id: "07280",
            name: "Metz",
            hot_records: [{ value: 39.5, date: "2000-08-10" }],
            cold_records: [{ value: -22.4, date: "1956-02-11" }],
        },
        {
            id: "07207",
            name: "Rennes",
            hot_records: [{ value: 40.3, date: "2019-06-27" }],
            cold_records: [{ value: -12.7, date: "1979-01-12" }],
        },
        {
            id: "07120",
            name: "Rouen",
            hot_records: [{ value: 41.7, date: "2019-07-25" }],
            cold_records: [{ value: -14.9, date: "1963-02-11" }],
        },
        {
            id: "07384",
            name: "Grenoble",
            hot_records: [{ value: 40.5, date: "2019-07-24" }],
            cold_records: [{ value: -20.7, date: "1971-02-10" }],
        },
        {
            id: "07747",
            name: "Toulon",
            hot_records: [{ value: 41.8, date: "2023-07-24" }],
            cold_records: [{ value: -5.8, date: "1956-01-09" }],
        },
        {
            id: "07790",
            name: "Nice",
            hot_records: [{ value: 37.2, date: "1983-07-22" }],
            cold_records: [{ value: -4.2, date: "1985-02-11" }],
        },
        {
            id: "07650",
            name: "Millau",
            hot_records: [{ value: 42.0, date: "2003-08-10" }],
            cold_records: [{ value: -15.6, date: "1963-02-11" }],
        },
        {
            id: "07560",
            name: "Biarritz",
            hot_records: [{ value: 40.5, date: "2019-06-28" }],
            cold_records: [{ value: -6.3, date: "1997-01-06" }],
        },
        {
            id: "07577",
            name: "Tarbes",
            hot_records: [{ value: 41.0, date: "2003-08-01" }],
            cold_records: [{ value: -13.8, date: "1956-02-03" }],
        },
        {
            id: "07761",
            name: "Ajaccio",
            hot_records: [{ value: 41.9, date: "1983-07-05" }],
            cold_records: [{ value: -3.5, date: "1971-02-01" }],
        },
        {
            id: "07015",
            name: "Brest",
            hot_records: [{ value: 36.4, date: "2022-06-18" }],
            cold_records: [{ value: -9.8, date: "1963-01-17" }],
        },
        {
            id: "07020",
            name: "Quimper",
            hot_records: [{ value: 37.2, date: "2019-06-27" }],
            cold_records: [{ value: -11.2, date: "1956-02-10" }],
        },
        {
            id: "07037",
            name: "Saint-Brieuc",
            hot_records: [{ value: 36.8, date: "2006-07-17" }],
            cold_records: [{ value: -10.4, date: "1987-01-12" }],
        },
        {
            id: "07057",
            name: "Caen",
            hot_records: [{ value: 40.3, date: "2019-07-25" }],
            cold_records: [{ value: -13.6, date: "1954-01-18" }],
        },
        {
            id: "07072",
            name: "Évreux",
            hot_records: [{ value: 41.5, date: "2019-07-25" }],
            cold_records: [{ value: -16.2, date: "1956-02-11" }],
        },
        {
            id: "07083",
            name: "Beauvais",
            hot_records: [{ value: 40.8, date: "1994-07-29" }],
            cold_records: [{ value: -17.1, date: "1985-01-09" }],
        },
        {
            id: "07168",
            name: "Troyes",
            hot_records: [{ value: 41.1, date: "2019-07-24" }],
            cold_records: [{ value: -19.3, date: "1963-02-06" }],
        },
        {
            id: "07174",
            name: "Auxerre",
            hot_records: [{ value: 40.7, date: "2003-08-11" }],
            cold_records: [{ value: -18.6, date: "1962-02-10" }],
        },
        {
            id: "07240",
            name: "Nevers",
            hot_records: [{ value: 41.3, date: "2003-08-11" }],
            cold_records: [{ value: -16.4, date: "1987-01-13" }],
        },
        {
            id: "07292",
            name: "Épinal",
            hot_records: [{ value: 38.9, date: "2015-07-06" }],
            cold_records: [{ value: -22.8, date: "1956-02-11" }],
        },
        {
            id: "07299",
            name: "Colmar",
            hot_records: [{ value: 40.2, date: "2019-07-25" }],
            cold_records: [{ value: -21.4, date: "1963-01-17" }],
        },
        {
            id: "07310",
            name: "Châlons-en-Champagne",
            hot_records: [{ value: 41.6, date: "2010-08-08" }],
            cold_records: [{ value: -20.5, date: "1956-02-11" }],
        },
        {
            id: "07350",
            name: "Mâcon",
            hot_records: [{ value: 40.9, date: "2003-08-12" }],
            cold_records: [{ value: -16.8, date: "1985-01-09" }],
        },
        {
            id: "07390",
            name: "Bourg-Saint-Maurice",
            hot_records: [{ value: 35.2, date: "2015-07-05" }],
            cold_records: [{ value: -27.4, date: "1956-02-11" }],
        },
        {
            id: "07422",
            name: "Le Puy-en-Velay",
            hot_records: [{ value: 38.1, date: "1983-08-01" }],
            cold_records: [{ value: -21.6, date: "1963-02-06" }],
        },
        {
            id: "07451",
            name: "Nîmes",
            hot_records: [{ value: 44.2, date: "2019-06-28" }],
            cold_records: [{ value: -8.6, date: "1971-02-04" }],
        },
        {
            id: "07471",
            name: "Aurillac",
            hot_records: [{ value: 39.4, date: "2003-08-12" }],
            cold_records: [{ value: -19.8, date: "1956-02-11" }],
        },
        {
            id: "07481",
            name: "Saint-Étienne",
            hot_records: [{ value: 39.8, date: "1976-07-20" }],
            cold_records: [{ value: -18.2, date: "1985-01-10" }],
        },
        {
            id: "07520",
            name: "Périgueux",
            hot_records: [{ value: 42.6, date: "2003-08-07" }],
            cold_records: [{ value: -10.8, date: "1963-02-03" }],
        },
        {
            id: "07535",
            name: "Cahors",
            hot_records: [{ value: 43.9, date: "1994-07-27" }],
            cold_records: [{ value: -11.4, date: "1956-02-04" }],
        },
        {
            id: "07558",
            name: "Mont-de-Marsan",
            hot_records: [{ value: 42.8, date: "2019-06-28" }],
            cold_records: [{ value: -9.6, date: "1985-01-09" }],
        },
        {
            id: "07591",
            name: "Auch",
            hot_records: [{ value: 43.1, date: "2003-08-06" }],
            cold_records: [{ value: -11.8, date: "1971-01-16" }],
        },
        {
            id: "07607",
            name: "Rodez",
            hot_records: [{ value: 41.3, date: "2022-07-19" }],
            cold_records: [{ value: -14.6, date: "1956-02-11" }],
        },
        {
            id: "07630",
            name: "Foix",
            hot_records: [{ value: 41.5, date: "2003-08-01" }],
            cold_records: [{ value: -13.2, date: "1963-02-03" }],
        },
        {
            id: "07643",
            name: "Carcassonne",
            hot_records: [{ value: 44.6, date: "2019-06-28" }],
            cold_records: [{ value: -9.2, date: "1974-01-15" }],
        },
        {
            id: "07661",
            name: "Albi",
            hot_records: [{ value: 43.5, date: "2003-08-06" }],
            cold_records: [{ value: -10.6, date: "1985-01-09" }],
        },
        {
            id: "07714",
            name: "Avignon",
            hot_records: [{ value: 43.8, date: "2019-06-28" }],
            cold_records: [{ value: -9.8, date: "1956-01-08" }],
        },
        {
            id: "07730",
            name: "Digne-les-Bains",
            hot_records: [{ value: 40.6, date: "2010-08-06" }],
            cold_records: [{ value: -16.4, date: "1956-02-10" }],
        },
        {
            id: "07760",
            name: "Draguignan",
            hot_records: [{ value: 43.2, date: "2023-07-24" }],
            cold_records: [{ value: -7.2, date: "1956-01-09" }],
        },
        {
            id: "07800",
            name: "Bastia",
            hot_records: [{ value: 40.3, date: "2017-07-12" }],
            cold_records: [{ value: -2.8, date: "1971-02-01" }],
        },
        {
            id: "07491",
            name: "Annecy",
            hot_records: [{ value: 38.6, date: "2019-07-25" }],
            cold_records: [{ value: -22.1, date: "1956-02-10" }],
        },
        {
            id: "07067",
            name: "Alençon",
            hot_records: [{ value: 40.6, date: "2006-07-18" }],
            cold_records: [{ value: -14.8, date: "1963-01-18" }],
        },
        {
            id: "07139",
            name: "Orléans",
            hot_records: [{ value: 41.4, date: "2003-08-11" }],
            cold_records: [{ value: -17.9, date: "1956-02-11" }],
        },
        {
            id: "07199",
            name: "Charleville-Mézières",
            hot_records: [{ value: 40.1, date: "2019-07-25" }],
            cold_records: [{ value: -21.8, date: "1956-02-11" }],
        },
        {
            id: "07313",
            name: "Bar-le-Duc",
            hot_records: [{ value: 39.6, date: "2000-08-09" }],
            cold_records: [{ value: -20.3, date: "1963-01-17" }],
        },
        {
            id: "07446",
            name: "Privas",
            hot_records: [{ value: 41.8, date: "2019-06-28" }],
            cold_records: [{ value: -12.4, date: "1956-02-11" }],
        },
        {
            id: "07553",
            name: "Limoges",
            hot_records: [{ value: 41.0, date: "1983-08-02" }],
            cold_records: [{ value: -13.6, date: "1985-02-03" }],
        },
        {
            id: "07569",
            name: "Angoulême",
            hot_records: [{ value: 42.2, date: "2003-08-07" }],
            cold_records: [{ value: -11.0, date: "1956-02-02" }],
        },
        {
            id: "07612",
            name: "Mende",
            hot_records: [{ value: 37.8, date: "1994-08-03" }],
            cold_records: [{ value: -18.6, date: "1956-02-11" }],
        },
        {
            id: "07900",
            name: "Béziers",
            hot_records: [{ value: 43.0, date: "1985-07-15" }],
            cold_records: [{ value: -8.0, date: "2003-01-05" }],
        },
        {
            id: "07901",
            name: "Narbonne",
            hot_records: [{ value: 42.5, date: "1985-07-16" }],
            cold_records: [{ value: -7.5, date: "2003-01-06" }],
        },
        {
            id: "07902",
            name: "Bagnols-sur-Cèze",
            hot_records: [{ value: 44.0, date: "1983-07-22" }],
            cold_records: [{ value: -9.0, date: "2019-02-01" }],
        },
        {
            id: "07903",
            name: "Valence",
            hot_records: [{ value: 41.6, date: "1976-07-18" }],
            cold_records: [{ value: -14.0, date: "2010-01-08" }],
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
