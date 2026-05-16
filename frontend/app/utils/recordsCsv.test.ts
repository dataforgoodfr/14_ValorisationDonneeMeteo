import { describe, expect, test } from "vitest";
import {
    buildRecordsCsv,
    getRecordKindLabels,
    buildPyramidRecordsCsv,
    buildScatterRecordsCsv,
} from "./recordsCsv";
import type {
    TemperatureRecordFlatEntry,
    TemperatureRecordsGraphRecord,
} from "~/types/api";

const makeRecord = (
    overrides: Partial<TemperatureRecordFlatEntry> = {},
): TemperatureRecordFlatEntry => ({
    station_id: "75114001",
    station_name: "Paris-Montsouris",
    department: "75",
    record_value: 42.6,
    record_date: "2019-06-28",
    lat: 0,
    lon: 0,
    alt: 75,
    classe_recente: 1,
    date_de_creation: "1872-01-01",
    ...overrides,
});

const HEADERS =
    "Station,Département,Record absolu (°C),Date du record,Classe,Altitude (m),Année de création";

describe("buildRecordsCsv", () => {
    test("tableau vide retourne uniquement les en-têtes", () => {
        const result = buildRecordsCsv([]);
        expect(result).toBe(`${HEADERS}\n`);
    });

    test("une ligne simple", () => {
        const result = buildRecordsCsv([makeRecord()]);
        expect(result).toBe(
            `${HEADERS}\nParis-Montsouris,75,42.6,2019-06-28,1,75,1872`,
        );
    });

    test("plusieurs stations", () => {
        const result = buildRecordsCsv([
            makeRecord(),
            makeRecord({
                station_name: "Lyon-Bron",
                department: "69",
                record_value: -15.2,
                record_date: "1985-01-05",
                alt: 200,
                classe_recente: 2,
                date_de_creation: "1920-03-15",
            }),
        ]);
        const lines = result.split("\n");
        expect(lines).toHaveLength(3);
        expect(lines[1]).toBe("Paris-Montsouris,75,42.6,2019-06-28,1,75,1872");
        expect(lines[2]).toBe("Lyon-Bron,69,-15.2,1985-01-05,2,200,1920");
    });

    test("nom de station avec virgule est entouré de guillemets", () => {
        const result = buildRecordsCsv([
            makeRecord({ station_name: "Saint-Jean, Haute-Loire" }),
        ]);
        expect(result).toContain('"Saint-Jean, Haute-Loire"');
    });

    test("valueLabel personnalisé remplace le header de valeur", () => {
        const result = buildRecordsCsv([makeRecord()], "Record battu (°C)");
        expect(result.startsWith("Station,Département,Record battu (°C)")).toBe(
            true,
        );
    });
});

describe("getRecordKindLabels", () => {
    test("historical → battus", () => {
        expect(getRecordKindLabels("historical")).toEqual({
            kindLabel: "records battus",
            kindFileLabel: "battus",
        });
    });

    test("autre valeur → absolus", () => {
        expect(getRecordKindLabels("absolute")).toEqual({
            kindLabel: "records absolus",
            kindFileLabel: "absolus",
        });
    });
});

const makePlot = (name: string, hotDates: string[], coldDates: string[]) => ({
    name,
    hot: hotDates.map((date) => ({ date, value: 40, station: "S" })),
    cold: coldDates.map((date) => ({ date, value: -5, station: "S" })),
});

describe("buildPyramidRecordsCsv", () => {
    test("headers corrects avec kindLabel", () => {
        const csv = buildPyramidRecordsCsv(
            [makePlot("IDF", ["2023-07"], [])],
            "records battus",
            "month",
        );
        expect(csv.split("\n")[0]).toBe(
            "Territoire,Période,Records de chaleur (records battus),Records de froid (records battus)",
        );
    });

    test("une ligne par période, triées", () => {
        const csv = buildPyramidRecordsCsv(
            [makePlot("IDF", ["2023-07"], ["2023-01"])],
            "records battus",
            "month",
        );
        const lines = csv.split("\n");
        expect(lines).toHaveLength(3);
        expect(lines[1]).toContain("2023-01");
        expect(lines[2]).toContain("2023-07");
    });

    test("compte correctement chaud et froid par période", () => {
        const csv = buildPyramidRecordsCsv(
            [makePlot("IDF", ["2023-07", "2023-07"], ["2023-07"])],
            "records battus",
            "month",
        );
        const dataLine = csv.split("\n")[1];
        expect(dataLine).toBe("IDF,2023-07,2,1");
    });

    test("nom de territoire avec virgule est entouré de guillemets", () => {
        const csv = buildPyramidRecordsCsv(
            [makePlot("Paris, IDF", ["2023-07"], [])],
            "records battus",
            "month",
        );
        expect(csv).toContain('"Paris, IDF"');
    });

    test("tableau vide — uniquement les en-têtes", () => {
        const csv = buildPyramidRecordsCsv([], "records absolus", "year");
        expect(csv).toBe(
            "Territoire,Période,Records de chaleur (records absolus),Records de froid (records absolus)",
        );
    });
});

const makeGraphRecord = (
    overrides: Partial<TemperatureRecordsGraphRecord> = {},
): TemperatureRecordsGraphRecord => ({
    date: "2023-07-14",
    station_id: "75001",
    station_name: "Paris",
    department: "75",
    type_records: "hot",
    valeur: 42.1,
    ...overrides,
});

describe("buildScatterRecordsCsv", () => {
    test("header chaleur correct", () => {
        const csv = buildScatterRecordsCsv([], "hot", "records battus");
        expect(csv).toBe(
            "Date,Température record de chaleur (records battus) (°C),Station,Département",
        );
    });

    test("header froid correct", () => {
        const csv = buildScatterRecordsCsv([], "cold", "records absolus");
        expect(csv).toBe(
            "Date,Température record de froid (records absolus) (°C),Station,Département",
        );
    });

    test("filtre uniquement les records hot", () => {
        const records = [
            makeGraphRecord({ type_records: "hot", date: "2023-07-14" }),
            makeGraphRecord({ type_records: "cold", date: "2023-01-10" }),
        ];
        const csv = buildScatterRecordsCsv(records, "hot", "records battus");
        expect(csv).toContain("2023-07-14");
        expect(csv).not.toContain("2023-01-10");
    });

    test("filtre uniquement les records cold", () => {
        const records = [
            makeGraphRecord({ type_records: "hot", date: "2023-07-14" }),
            makeGraphRecord({ type_records: "cold", date: "2023-01-10" }),
        ];
        const csv = buildScatterRecordsCsv(records, "cold", "records battus");
        expect(csv).toContain("2023-01-10");
        expect(csv).not.toContain("2023-07-14");
    });

    test("nom de station avec virgule est entouré de guillemets", () => {
        const csv = buildScatterRecordsCsv(
            [makeGraphRecord({ station_name: "Paris, Gare" })],
            "hot",
            "records battus",
        );
        expect(csv).toContain('"Paris, Gare"');
    });
});
