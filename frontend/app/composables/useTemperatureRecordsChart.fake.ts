import type {
    TemperatureRecordsParams,
    TemperatureRecordsResponse,
} from "~/types/api";

const fakeResponse: TemperatureRecordsResponse = {
    count: 0,
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
            departement: 94,
            hot_records: [
                {
                    station_id: "07149",
                    station_name: "Orly",
                    department: "94",
                    record_value: 42.1,
                    record_date: "2003-08-12",
                },
            ],
            cold_records: [
                {
                    station_id: "07149",
                    station_name: "Orly",
                    department: "94",
                    record_value: -7.2,
                    record_date: "1980-01-15",
                },
            ],
        },
        {
            id: "75114001",
            name: "Paris-Montsouris",
            departement: 75,
            hot_records: [
                {
                    station_id: "75114001",
                    station_name: "Paris-Montsouris",
                    department: "75",
                    record_value: 40.4,
                    record_date: "2019-07-25",
                },
            ],
            cold_records: [
                {
                    station_id: "75114001",
                    station_name: "Paris-Montsouris",
                    department: "75",
                    record_value: -11.4,
                    record_date: "1956-02-10",
                },
            ],
        },
        {
            id: "07181",
            name: "Melun",
            departement: 77,
            hot_records: [
                {
                    station_id: "07181",
                    station_name: "Melun",
                    department: "77",
                    record_value: 38.0,
                    record_date: "1976-07-19",
                },
            ],
            cold_records: [
                {
                    station_id: "07181",
                    station_name: "Melun",
                    department: "77",
                    record_value: -16.0,
                    record_date: "1968-01-19",
                },
            ],
        },
        {
            id: "07222",
            name: "Tours",
            departement: 37,
            hot_records: [
                {
                    station_id: "07222",
                    station_name: "Tours",
                    department: "37",
                    record_value: 41.2,
                    record_date: "2003-08-09",
                },
            ],
            cold_records: [
                {
                    station_id: "07222",
                    station_name: "Tours",
                    department: "37",
                    record_value: -14.3,
                    record_date: "1985-02-03",
                },
            ],
        },
        {
            id: "07460",
            name: "Marseille-Marignane",
            departement: 13,
            hot_records: [
                {
                    station_id: "07460",
                    station_name: "Marseille-Marignane",
                    department: "13",
                    record_value: 44.1,
                    record_date: "2023-07-24",
                },
            ],
            cold_records: [
                {
                    station_id: "07460",
                    station_name: "Marseille-Marignane",
                    department: "13",
                    record_value: -10.6,
                    record_date: "1956-01-08",
                },
            ],
        },
        {
            id: "07510",
            name: "Bordeaux-Mérignac",
            departement: 33,
            hot_records: [
                {
                    station_id: "07510",
                    station_name: "Bordeaux-Mérignac",
                    department: "33",
                    record_value: 42.4,
                    record_date: "2019-06-28",
                },
            ],
            cold_records: [
                {
                    station_id: "07510",
                    station_name: "Bordeaux-Mérignac",
                    department: "33",
                    record_value: -11.6,
                    record_date: "1971-01-16",
                },
            ],
        },
        {
            id: "07130",
            name: "Lille-Lesquin",
            departement: 59,
            hot_records: [
                {
                    station_id: "07130",
                    station_name: "Lille-Lesquin",
                    department: "59",
                    record_value: 38.5,
                    record_date: "2006-07-19",
                },
            ],
            cold_records: [
                {
                    station_id: "07130",
                    station_name: "Lille-Lesquin",
                    department: "59",
                    record_value: -15.5,
                    record_date: "1987-01-13",
                },
            ],
        },
        {
            id: "07480",
            name: "Lyon-Bron",
            departement: 69,
            hot_records: [
                {
                    station_id: "07480",
                    station_name: "Lyon-Bron",
                    department: "69",
                    record_value: 41.9,
                    record_date: "2019-06-28",
                },
            ],
            cold_records: [
                {
                    station_id: "07480",
                    station_name: "Lyon-Bron",
                    department: "69",
                    record_value: -18.8,
                    record_date: "1963-02-10",
                },
            ],
        },
        {
            id: "07690",
            name: "Toulouse-Blagnac",
            departement: 31,
            hot_records: [
                {
                    station_id: "07690",
                    station_name: "Toulouse-Blagnac",
                    department: "31",
                    record_value: 43.3,
                    record_date: "2003-08-01",
                },
            ],
            cold_records: [
                {
                    station_id: "07690",
                    station_name: "Toulouse-Blagnac",
                    department: "31",
                    record_value: -12.6,
                    record_date: "1974-02-03",
                },
            ],
        },
        {
            id: "07371",
            name: "Strasbourg",
            departement: 67,
            hot_records: [
                {
                    station_id: "07371",
                    station_name: "Strasbourg",
                    department: "67",
                    record_value: 39.7,
                    record_date: "2015-07-05",
                },
            ],
            cold_records: [
                {
                    station_id: "07371",
                    station_name: "Strasbourg",
                    department: "67",
                    record_value: -23.6,
                    record_date: "1956-02-11",
                },
            ],
        },
        {
            id: "07230",
            name: "Clermont-Ferrand",
            departement: 63,
            hot_records: [
                {
                    station_id: "07230",
                    station_name: "Clermont-Ferrand",
                    department: "63",
                    record_value: 40.8,
                    record_date: "2003-08-12",
                },
            ],
            cold_records: [
                {
                    station_id: "07230",
                    station_name: "Clermont-Ferrand",
                    department: "63",
                    record_value: -17.2,
                    record_date: "1971-02-11",
                },
            ],
        },
        {
            id: "07434",
            name: "Montpellier",
            departement: 34,
            hot_records: [
                {
                    station_id: "07434",
                    station_name: "Montpellier",
                    department: "34",
                    record_value: 43.4,
                    record_date: "2019-06-28",
                },
            ],
            cold_records: [
                {
                    station_id: "07434",
                    station_name: "Montpellier",
                    department: "34",
                    record_value: -9.4,
                    record_date: "1991-02-04",
                },
            ],
        },
        {
            id: "07110",
            name: "Cherbourg",
            departement: 50,
            hot_records: [
                {
                    station_id: "07110",
                    station_name: "Cherbourg",
                    department: "50",
                    record_value: 35.3,
                    record_date: "2022-06-17",
                },
            ],
            cold_records: [
                {
                    station_id: "07110",
                    station_name: "Cherbourg",
                    department: "50",
                    record_value: -8.1,
                    record_date: "1963-02-18",
                },
            ],
        },
        {
            id: "07335",
            name: "Dijon",
            departement: 21,
            hot_records: [
                {
                    station_id: "07335",
                    station_name: "Dijon",
                    department: "21",
                    record_value: 40.6,
                    record_date: "2019-07-24",
                },
            ],
            cold_records: [
                {
                    station_id: "07335",
                    station_name: "Dijon",
                    department: "21",
                    record_value: -19.5,
                    record_date: "1956-02-10",
                },
            ],
        },
        {
            id: "07190",
            name: "Reims",
            departement: 51,
            hot_records: [
                {
                    station_id: "07190",
                    station_name: "Reims",
                    department: "51",
                    record_value: 41.9,
                    record_date: "2010-08-07",
                },
            ],
            cold_records: [
                {
                    station_id: "07190",
                    station_name: "Reims",
                    department: "51",
                    record_value: -20.1,
                    record_date: "1963-02-11",
                },
            ],
        },
        {
            id: "07255",
            name: "Bourges",
            departement: 18,
            hot_records: [
                {
                    station_id: "07255",
                    station_name: "Bourges",
                    department: "18",
                    record_value: 41.7,
                    record_date: "2003-08-11",
                },
            ],
            cold_records: [
                {
                    station_id: "07255",
                    station_name: "Bourges",
                    department: "18",
                    record_value: -16.8,
                    record_date: "1977-01-18",
                },
            ],
        },
        {
            id: "07540",
            name: "Agen",
            departement: 47,
            hot_records: [
                {
                    station_id: "07540",
                    station_name: "Agen",
                    department: "47",
                    record_value: 43.7,
                    record_date: "1994-07-28",
                },
            ],
            cold_records: [
                {
                    station_id: "07540",
                    station_name: "Agen",
                    department: "47",
                    record_value: -10.3,
                    record_date: "1956-02-04",
                },
            ],
        },
        {
            id: "07699",
            name: "Perpignan",
            departement: 66,
            hot_records: [
                {
                    station_id: "07699",
                    station_name: "Perpignan",
                    department: "66",
                    record_value: 45.3,
                    record_date: "2023-07-17",
                },
            ],
            cold_records: [
                {
                    station_id: "07699",
                    station_name: "Perpignan",
                    department: "66",
                    record_value: -8.7,
                    record_date: "1960-02-02",
                },
            ],
        },
        {
            id: "07270",
            name: "Nancy",
            departement: 54,
            hot_records: [
                {
                    station_id: "07270",
                    station_name: "Nancy",
                    department: "54",
                    record_value: 39.8,
                    record_date: "2019-07-25",
                },
            ],
            cold_records: [
                {
                    station_id: "07270",
                    station_name: "Nancy",
                    department: "54",
                    record_value: -21.3,
                    record_date: "1956-02-11",
                },
            ],
        },
        {
            id: "07145",
            name: "Chartres",
            departement: 28,
            hot_records: [
                {
                    station_id: "07145",
                    station_name: "Chartres",
                    department: "28",
                    record_value: 40.1,
                    record_date: "2019-07-25",
                },
            ],
            cold_records: [
                {
                    station_id: "07145",
                    station_name: "Chartres",
                    department: "28",
                    record_value: -18.4,
                    record_date: "1963-02-11",
                },
            ],
        },
        {
            id: "07620",
            name: "Pau",
            departement: 64,
            hot_records: [
                {
                    station_id: "07620",
                    station_name: "Pau",
                    department: "64",
                    record_value: 42.9,
                    record_date: "2019-06-28",
                },
            ],
            cold_records: [
                {
                    station_id: "07620",
                    station_name: "Pau",
                    department: "64",
                    record_value: -10.9,
                    record_date: "1985-02-03",
                },
            ],
        },
        {
            id: "07280",
            name: "Metz",
            departement: 57,
            hot_records: [
                {
                    station_id: "07280",
                    station_name: "Metz",
                    department: "57",
                    record_value: 39.5,
                    record_date: "2000-08-10",
                },
            ],
            cold_records: [
                {
                    station_id: "07280",
                    station_name: "Metz",
                    department: "57",
                    record_value: -22.4,
                    record_date: "1956-02-11",
                },
            ],
        },
        {
            id: "07207",
            name: "Rennes",
            departement: 35,
            hot_records: [
                {
                    station_id: "07207",
                    station_name: "Rennes",
                    department: "35",
                    record_value: 40.3,
                    record_date: "2019-06-27",
                },
            ],
            cold_records: [
                {
                    station_id: "07207",
                    station_name: "Rennes",
                    department: "35",
                    record_value: -12.7,
                    record_date: "1979-01-12",
                },
            ],
        },
        {
            id: "07120",
            name: "Rouen",
            departement: 76,
            hot_records: [
                {
                    station_id: "07120",
                    station_name: "Rouen",
                    department: "76",
                    record_value: 41.7,
                    record_date: "2019-07-25",
                },
            ],
            cold_records: [
                {
                    station_id: "07120",
                    station_name: "Rouen",
                    department: "76",
                    record_value: -14.9,
                    record_date: "1963-02-11",
                },
            ],
        },
        {
            id: "07384",
            name: "Grenoble",
            departement: 38,
            hot_records: [
                {
                    station_id: "07384",
                    station_name: "Grenoble",
                    department: "38",
                    record_value: 40.5,
                    record_date: "2019-07-24",
                },
            ],
            cold_records: [
                {
                    station_id: "07384",
                    station_name: "Grenoble",
                    department: "38",
                    record_value: -20.7,
                    record_date: "1971-02-10",
                },
            ],
        },
        {
            id: "07747",
            name: "Toulon",
            departement: 83,
            hot_records: [
                {
                    station_id: "07747",
                    station_name: "Toulon",
                    department: "83",
                    record_value: 41.8,
                    record_date: "2023-07-24",
                },
            ],
            cold_records: [
                {
                    station_id: "07747",
                    station_name: "Toulon",
                    department: "83",
                    record_value: -5.8,
                    record_date: "1956-01-09",
                },
            ],
        },
        {
            id: "07790",
            name: "Nice",
            departement: 6,
            hot_records: [
                {
                    station_id: "07790",
                    station_name: "Nice",
                    department: "6",
                    record_value: 37.2,
                    record_date: "1983-07-22",
                },
            ],
            cold_records: [
                {
                    station_id: "07790",
                    station_name: "Nice",
                    department: "6",
                    record_value: -4.2,
                    record_date: "1985-02-11",
                },
            ],
        },
        {
            id: "07650",
            name: "Millau",
            departement: 12,
            hot_records: [
                {
                    station_id: "07650",
                    station_name: "Millau",
                    department: "12",
                    record_value: 42.0,
                    record_date: "2003-08-10",
                },
            ],
            cold_records: [
                {
                    station_id: "07650",
                    station_name: "Millau",
                    department: "12",
                    record_value: -15.6,
                    record_date: "1963-02-11",
                },
            ],
        },
        {
            id: "07560",
            name: "Biarritz",
            departement: 64,
            hot_records: [
                {
                    station_id: "07560",
                    station_name: "Biarritz",
                    department: "64",
                    record_value: 40.5,
                    record_date: "2019-06-28",
                },
            ],
            cold_records: [
                {
                    station_id: "07560",
                    station_name: "Biarritz",
                    department: "64",
                    record_value: -6.3,
                    record_date: "1997-01-06",
                },
            ],
        },
        {
            id: "07577",
            name: "Tarbes",
            departement: 65,
            hot_records: [
                {
                    station_id: "07577",
                    station_name: "Tarbes",
                    department: "65",
                    record_value: 41.0,
                    record_date: "2003-08-01",
                },
            ],
            cold_records: [
                {
                    station_id: "07577",
                    station_name: "Tarbes",
                    department: "65",
                    record_value: -13.8,
                    record_date: "1956-02-03",
                },
            ],
        },
        {
            id: "07761",
            name: "Ajaccio",
            departement: 20,
            hot_records: [
                {
                    station_id: "07761",
                    station_name: "Ajaccio",
                    department: "20",
                    record_value: 41.9,
                    record_date: "1983-07-05",
                },
            ],
            cold_records: [
                {
                    station_id: "07761",
                    station_name: "Ajaccio",
                    department: "20",
                    record_value: -3.5,
                    record_date: "1971-02-01",
                },
            ],
        },
        {
            id: "07015",
            name: "Brest",
            departement: 29,
            hot_records: [
                {
                    station_id: "07015",
                    station_name: "Brest",
                    department: "29",
                    record_value: 36.4,
                    record_date: "2022-06-18",
                },
            ],
            cold_records: [
                {
                    station_id: "07015",
                    station_name: "Brest",
                    department: "29",
                    record_value: -9.8,
                    record_date: "1963-01-17",
                },
            ],
        },
        {
            id: "07020",
            name: "Quimper",
            departement: 29,
            hot_records: [
                {
                    station_id: "07020",
                    station_name: "Quimper",
                    department: "29",
                    record_value: 37.2,
                    record_date: "2019-06-27",
                },
            ],
            cold_records: [
                {
                    station_id: "07020",
                    station_name: "Quimper",
                    department: "29",
                    record_value: -11.2,
                    record_date: "1956-02-10",
                },
            ],
        },
        {
            id: "07037",
            name: "Saint-Brieuc",
            departement: 22,
            hot_records: [
                {
                    station_id: "07037",
                    station_name: "Saint-Brieuc",
                    department: "22",
                    record_value: 36.8,
                    record_date: "2006-07-17",
                },
            ],
            cold_records: [
                {
                    station_id: "07037",
                    station_name: "Saint-Brieuc",
                    department: "22",
                    record_value: -10.4,
                    record_date: "1987-01-12",
                },
            ],
        },
        {
            id: "07057",
            name: "Caen",
            departement: 14,
            hot_records: [
                {
                    station_id: "07057",
                    station_name: "Caen",
                    department: "14",
                    record_value: 40.3,
                    record_date: "2019-07-25",
                },
            ],
            cold_records: [
                {
                    station_id: "07057",
                    station_name: "Caen",
                    department: "14",
                    record_value: -13.6,
                    record_date: "1954-01-18",
                },
            ],
        },
        {
            id: "07072",
            name: "Évreux",
            departement: 27,
            hot_records: [
                {
                    station_id: "07072",
                    station_name: "Évreux",
                    department: "27",
                    record_value: 41.5,
                    record_date: "2019-07-25",
                },
            ],
            cold_records: [
                {
                    station_id: "07072",
                    station_name: "Évreux",
                    department: "27",
                    record_value: -16.2,
                    record_date: "1956-02-11",
                },
            ],
        },
        {
            id: "07083",
            name: "Beauvais",
            departement: 60,
            hot_records: [
                {
                    station_id: "07083",
                    station_name: "Beauvais",
                    department: "60",
                    record_value: 40.8,
                    record_date: "1994-07-29",
                },
            ],
            cold_records: [
                {
                    station_id: "07083",
                    station_name: "Beauvais",
                    department: "60",
                    record_value: -17.1,
                    record_date: "1985-01-09",
                },
            ],
        },
        {
            id: "07168",
            name: "Troyes",
            departement: 10,
            hot_records: [
                {
                    station_id: "07168",
                    station_name: "Troyes",
                    department: "10",
                    record_value: 41.1,
                    record_date: "2019-07-24",
                },
            ],
            cold_records: [
                {
                    station_id: "07168",
                    station_name: "Troyes",
                    department: "10",
                    record_value: -19.3,
                    record_date: "1963-02-06",
                },
            ],
        },
        {
            id: "07174",
            name: "Auxerre",
            departement: 89,
            hot_records: [
                {
                    station_id: "07174",
                    station_name: "Auxerre",
                    department: "89",
                    record_value: 40.7,
                    record_date: "2003-08-11",
                },
            ],
            cold_records: [
                {
                    station_id: "07174",
                    station_name: "Auxerre",
                    department: "89",
                    record_value: -18.6,
                    record_date: "1962-02-10",
                },
            ],
        },
        {
            id: "07240",
            name: "Nevers",
            departement: 58,
            hot_records: [
                {
                    station_id: "07240",
                    station_name: "Nevers",
                    department: "58",
                    record_value: 41.3,
                    record_date: "2003-08-11",
                },
            ],
            cold_records: [
                {
                    station_id: "07240",
                    station_name: "Nevers",
                    department: "58",
                    record_value: -16.4,
                    record_date: "1987-01-13",
                },
            ],
        },
        {
            id: "07292",
            name: "Épinal",
            departement: 88,
            hot_records: [
                {
                    station_id: "07292",
                    station_name: "Épinal",
                    department: "88",
                    record_value: 38.9,
                    record_date: "2015-07-06",
                },
            ],
            cold_records: [
                {
                    station_id: "07292",
                    station_name: "Épinal",
                    department: "88",
                    record_value: -22.8,
                    record_date: "1956-02-11",
                },
            ],
        },
        {
            id: "07299",
            name: "Colmar",
            departement: 68,
            hot_records: [
                {
                    station_id: "07299",
                    station_name: "Colmar",
                    department: "68",
                    record_value: 40.2,
                    record_date: "2019-07-25",
                },
            ],
            cold_records: [
                {
                    station_id: "07299",
                    station_name: "Colmar",
                    department: "68",
                    record_value: -21.4,
                    record_date: "1963-01-17",
                },
            ],
        },
        {
            id: "07310",
            name: "Châlons-en-Champagne",
            departement: 51,
            hot_records: [
                {
                    station_id: "07310",
                    station_name: "Châlons-en-Champagne",
                    department: "51",
                    record_value: 41.6,
                    record_date: "2010-08-08",
                },
            ],
            cold_records: [
                {
                    station_id: "07310",
                    station_name: "Châlons-en-Champagne",
                    department: "51",
                    record_value: -20.5,
                    record_date: "1956-02-11",
                },
            ],
        },
        {
            id: "07350",
            name: "Mâcon",
            departement: 71,
            hot_records: [
                {
                    station_id: "07350",
                    station_name: "Mâcon",
                    department: "71",
                    record_value: 40.9,
                    record_date: "2003-08-12",
                },
            ],
            cold_records: [
                {
                    station_id: "07350",
                    station_name: "Mâcon",
                    department: "71",
                    record_value: -16.8,
                    record_date: "1985-01-09",
                },
            ],
        },
        {
            id: "07390",
            name: "Bourg-Saint-Maurice",
            departement: 73,
            hot_records: [
                {
                    station_id: "07390",
                    station_name: "Bourg-Saint-Maurice",
                    department: "73",
                    record_value: 35.2,
                    record_date: "2015-07-05",
                },
            ],
            cold_records: [
                {
                    station_id: "07390",
                    station_name: "Bourg-Saint-Maurice",
                    department: "73",
                    record_value: -27.4,
                    record_date: "1956-02-11",
                },
            ],
        },
        {
            id: "07422",
            name: "Le Puy-en-Velay",
            departement: 43,
            hot_records: [
                {
                    station_id: "07422",
                    station_name: "Le Puy-en-Velay",
                    department: "43",
                    record_value: 38.1,
                    record_date: "1983-08-01",
                },
            ],
            cold_records: [
                {
                    station_id: "07422",
                    station_name: "Le Puy-en-Velay",
                    department: "43",
                    record_value: -21.6,
                    record_date: "1963-02-06",
                },
            ],
        },
        {
            id: "07451",
            name: "Nîmes",
            departement: 30,
            hot_records: [
                {
                    station_id: "07451",
                    station_name: "Nîmes",
                    department: "30",
                    record_value: 44.2,
                    record_date: "2019-06-28",
                },
            ],
            cold_records: [
                {
                    station_id: "07451",
                    station_name: "Nîmes",
                    department: "30",
                    record_value: -8.6,
                    record_date: "1971-02-04",
                },
            ],
        },
        {
            id: "07471",
            name: "Aurillac",
            departement: 15,
            hot_records: [
                {
                    station_id: "07471",
                    station_name: "Aurillac",
                    department: "15",
                    record_value: 39.4,
                    record_date: "2003-08-12",
                },
            ],
            cold_records: [
                {
                    station_id: "07471",
                    station_name: "Aurillac",
                    department: "15",
                    record_value: -19.8,
                    record_date: "1956-02-11",
                },
            ],
        },
        {
            id: "07481",
            name: "Saint-Étienne",
            departement: 42,
            hot_records: [
                {
                    station_id: "07481",
                    station_name: "Saint-Étienne",
                    department: "42",
                    record_value: 39.8,
                    record_date: "1976-07-20",
                },
            ],
            cold_records: [
                {
                    station_id: "07481",
                    station_name: "Saint-Étienne",
                    department: "42",
                    record_value: -18.2,
                    record_date: "1985-01-10",
                },
            ],
        },
        {
            id: "07520",
            name: "Périgueux",
            departement: 24,
            hot_records: [
                {
                    station_id: "07520",
                    station_name: "Périgueux",
                    department: "24",
                    record_value: 42.6,
                    record_date: "2003-08-07",
                },
            ],
            cold_records: [
                {
                    station_id: "07520",
                    station_name: "Périgueux",
                    department: "24",
                    record_value: -10.8,
                    record_date: "1963-02-03",
                },
            ],
        },
        {
            id: "07535",
            name: "Cahors",
            departement: 46,
            hot_records: [
                {
                    station_id: "07535",
                    station_name: "Cahors",
                    department: "46",
                    record_value: 43.9,
                    record_date: "1994-07-27",
                },
            ],
            cold_records: [
                {
                    station_id: "07535",
                    station_name: "Cahors",
                    department: "46",
                    record_value: -11.4,
                    record_date: "1956-02-04",
                },
            ],
        },
        {
            id: "07558",
            name: "Mont-de-Marsan",
            departement: 40,
            hot_records: [
                {
                    station_id: "07558",
                    station_name: "Mont-de-Marsan",
                    department: "40",
                    record_value: 42.8,
                    record_date: "2019-06-28",
                },
            ],
            cold_records: [
                {
                    station_id: "07558",
                    station_name: "Mont-de-Marsan",
                    department: "40",
                    record_value: -9.6,
                    record_date: "1985-01-09",
                },
            ],
        },
        {
            id: "07591",
            name: "Auch",
            departement: 32,
            hot_records: [
                {
                    station_id: "07591",
                    station_name: "Auch",
                    department: "32",
                    record_value: 43.1,
                    record_date: "2003-08-06",
                },
            ],
            cold_records: [
                {
                    station_id: "07591",
                    station_name: "Auch",
                    department: "32",
                    record_value: -11.8,
                    record_date: "1971-01-16",
                },
            ],
        },
        {
            id: "07607",
            name: "Rodez",
            departement: 12,
            hot_records: [
                {
                    station_id: "07607",
                    station_name: "Rodez",
                    department: "12",
                    record_value: 41.3,
                    record_date: "2022-07-19",
                },
            ],
            cold_records: [
                {
                    station_id: "07607",
                    station_name: "Rodez",
                    department: "12",
                    record_value: -14.6,
                    record_date: "1956-02-11",
                },
            ],
        },
        {
            id: "07630",
            name: "Foix",
            departement: 9,
            hot_records: [
                {
                    station_id: "07630",
                    station_name: "Foix",
                    department: "9",
                    record_value: 41.5,
                    record_date: "2003-08-01",
                },
            ],
            cold_records: [
                {
                    station_id: "07630",
                    station_name: "Foix",
                    department: "9",
                    record_value: -13.2,
                    record_date: "1963-02-03",
                },
            ],
        },
        {
            id: "07643",
            name: "Carcassonne",
            departement: 11,
            hot_records: [
                {
                    station_id: "07643",
                    station_name: "Carcassonne",
                    department: "11",
                    record_value: 44.6,
                    record_date: "2019-06-28",
                },
            ],
            cold_records: [
                {
                    station_id: "07643",
                    station_name: "Carcassonne",
                    department: "11",
                    record_value: -9.2,
                    record_date: "1974-01-15",
                },
            ],
        },
        {
            id: "07661",
            name: "Albi",
            departement: 81,
            hot_records: [
                {
                    station_id: "07661",
                    station_name: "Albi",
                    department: "81",
                    record_value: 43.5,
                    record_date: "2003-08-06",
                },
            ],
            cold_records: [
                {
                    station_id: "07661",
                    station_name: "Albi",
                    department: "81",
                    record_value: -10.6,
                    record_date: "1985-01-09",
                },
            ],
        },
        {
            id: "07714",
            name: "Avignon",
            departement: 84,
            hot_records: [
                {
                    station_id: "07714",
                    station_name: "Avignon",
                    department: "84",
                    record_value: 43.8,
                    record_date: "2019-06-28",
                },
            ],
            cold_records: [
                {
                    station_id: "07714",
                    station_name: "Avignon",
                    department: "84",
                    record_value: -9.8,
                    record_date: "1956-01-08",
                },
            ],
        },
        {
            id: "07730",
            name: "Digne-les-Bains",
            departement: 4,
            hot_records: [
                {
                    station_id: "07730",
                    station_name: "Digne-les-Bains",
                    department: "4",
                    record_value: 40.6,
                    record_date: "2010-08-06",
                },
            ],
            cold_records: [
                {
                    station_id: "07730",
                    station_name: "Digne-les-Bains",
                    department: "4",
                    record_value: -16.4,
                    record_date: "1956-02-10",
                },
            ],
        },
        {
            id: "07760",
            name: "Draguignan",
            departement: 83,
            hot_records: [
                {
                    station_id: "07760",
                    station_name: "Draguignan",
                    department: "83",
                    record_value: 43.2,
                    record_date: "2023-07-24",
                },
            ],
            cold_records: [
                {
                    station_id: "07760",
                    station_name: "Draguignan",
                    department: "83",
                    record_value: -7.2,
                    record_date: "1956-01-09",
                },
            ],
        },
        {
            id: "07800",
            name: "Bastia",
            departement: 20,
            hot_records: [
                {
                    station_id: "07800",
                    station_name: "Bastia",
                    department: "20",
                    record_value: 40.3,
                    record_date: "2017-07-12",
                },
            ],
            cold_records: [
                {
                    station_id: "07800",
                    station_name: "Bastia",
                    department: "20",
                    record_value: -2.8,
                    record_date: "1971-02-01",
                },
            ],
        },
        {
            id: "07491",
            name: "Annecy",
            departement: 74,
            hot_records: [
                {
                    station_id: "07491",
                    station_name: "Annecy",
                    department: "74",
                    record_value: 38.6,
                    record_date: "2019-07-25",
                },
            ],
            cold_records: [
                {
                    station_id: "07491",
                    station_name: "Annecy",
                    department: "74",
                    record_value: -22.1,
                    record_date: "1956-02-10",
                },
            ],
        },
        {
            id: "07067",
            name: "Alençon",
            departement: 61,
            hot_records: [
                {
                    station_id: "07067",
                    station_name: "Alençon",
                    department: "61",
                    record_value: 40.6,
                    record_date: "2006-07-18",
                },
            ],
            cold_records: [
                {
                    station_id: "07067",
                    station_name: "Alençon",
                    department: "61",
                    record_value: -14.8,
                    record_date: "1963-01-18",
                },
            ],
        },
        {
            id: "07139",
            name: "Orléans",
            departement: 45,
            hot_records: [
                {
                    station_id: "07139",
                    station_name: "Orléans",
                    department: "45",
                    record_value: 41.4,
                    record_date: "2003-08-11",
                },
            ],
            cold_records: [
                {
                    station_id: "07139",
                    station_name: "Orléans",
                    department: "45",
                    record_value: -17.9,
                    record_date: "1956-02-11",
                },
            ],
        },
        {
            id: "07199",
            name: "Charleville-Mézières",
            departement: 8,
            hot_records: [
                {
                    station_id: "07199",
                    station_name: "Charleville-Mézières",
                    department: "8",
                    record_value: 40.1,
                    record_date: "2019-07-25",
                },
            ],
            cold_records: [
                {
                    station_id: "07199",
                    station_name: "Charleville-Mézières",
                    department: "8",
                    record_value: -21.8,
                    record_date: "1956-02-11",
                },
            ],
        },
        {
            id: "07313",
            name: "Bar-le-Duc",
            departement: 55,
            hot_records: [
                {
                    station_id: "07313",
                    station_name: "Bar-le-Duc",
                    department: "55",
                    record_value: 39.6,
                    record_date: "2000-08-09",
                },
            ],
            cold_records: [
                {
                    station_id: "07313",
                    station_name: "Bar-le-Duc",
                    department: "55",
                    record_value: -20.3,
                    record_date: "1963-01-17",
                },
            ],
        },
        {
            id: "07446",
            name: "Privas",
            departement: 7,
            hot_records: [
                {
                    station_id: "07446",
                    station_name: "Privas",
                    department: "7",
                    record_value: 41.8,
                    record_date: "2019-06-28",
                },
            ],
            cold_records: [
                {
                    station_id: "07446",
                    station_name: "Privas",
                    department: "7",
                    record_value: -12.4,
                    record_date: "1956-02-11",
                },
            ],
        },
        {
            id: "07553",
            name: "Limoges",
            departement: 87,
            hot_records: [
                {
                    station_id: "07553",
                    station_name: "Limoges",
                    department: "87",
                    record_value: 41.0,
                    record_date: "1983-08-02",
                },
            ],
            cold_records: [
                {
                    station_id: "07553",
                    station_name: "Limoges",
                    department: "87",
                    record_value: -13.6,
                    record_date: "1985-02-03",
                },
            ],
        },
        {
            id: "07569",
            name: "Angoulême",
            departement: 16,
            hot_records: [
                {
                    station_id: "07569",
                    station_name: "Angoulême",
                    department: "16",
                    record_value: 42.2,
                    record_date: "2003-08-07",
                },
            ],
            cold_records: [
                {
                    station_id: "07569",
                    station_name: "Angoulême",
                    department: "16",
                    record_value: -11.0,
                    record_date: "1956-02-02",
                },
            ],
        },
        {
            id: "07612",
            name: "Mende",
            departement: 48,
            hot_records: [
                {
                    station_id: "07612",
                    station_name: "Mende",
                    department: "48",
                    record_value: 37.8,
                    record_date: "1994-08-03",
                },
            ],
            cold_records: [
                {
                    station_id: "07612",
                    station_name: "Mende",
                    department: "48",
                    record_value: -18.6,
                    record_date: "1956-02-11",
                },
            ],
        },
        {
            id: "07900",
            name: "Béziers",
            departement: 34,
            hot_records: [
                {
                    station_id: "07900",
                    station_name: "Béziers",
                    department: "34",
                    record_value: 43.0,
                    record_date: "1985-07-15",
                },
            ],
            cold_records: [
                {
                    station_id: "07900",
                    station_name: "Béziers",
                    department: "34",
                    record_value: -8.0,
                    record_date: "2003-01-05",
                },
            ],
        },
        {
            id: "07901",
            name: "Narbonne",
            departement: 11,
            hot_records: [
                {
                    station_id: "07901",
                    station_name: "Narbonne",
                    department: "11",
                    record_value: 42.5,
                    record_date: "1985-07-16",
                },
            ],
            cold_records: [
                {
                    station_id: "07901",
                    station_name: "Narbonne",
                    department: "11",
                    record_value: -7.5,
                    record_date: "2003-01-06",
                },
            ],
        },
        {
            id: "07902",
            name: "Bagnols-sur-Cèze",
            departement: 30,
            hot_records: [
                {
                    station_id: "07902",
                    station_name: "Bagnols-sur-Cèze",
                    department: "30",
                    record_value: 44.0,
                    record_date: "1983-07-22",
                },
            ],
            cold_records: [
                {
                    station_id: "07902",
                    station_name: "Bagnols-sur-Cèze",
                    department: "30",
                    record_value: -9.0,
                    record_date: "2019-02-01",
                },
            ],
        },
        {
            id: "07903",
            name: "Valence",
            departement: 26,
            hot_records: [
                {
                    station_id: "07903",
                    station_name: "Valence",
                    department: "26",
                    record_value: 41.6,
                    record_date: "1976-07-18",
                },
            ],
            cold_records: [
                {
                    station_id: "07903",
                    station_name: "Valence",
                    department: "26",
                    record_value: -14.0,
                    record_date: "2010-01-08",
                },
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
                        (!date_start || r.record_date >= date_start) &&
                        (!date_end || r.record_date <= date_end),
                ),
                cold_records: station.cold_records.filter(
                    (r) =>
                        (!date_start || r.record_date >= date_start) &&
                        (!date_end || r.record_date <= date_end),
                ),
            }))
            .filter(
                (s) => s.hot_records.length > 0 || s.cold_records.length > 0,
            );

        return {
            count: stations.reduce(
                (acc, s) => acc + s.hot_records.length + s.cold_records.length,
                0,
            ),
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
