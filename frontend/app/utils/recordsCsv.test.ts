import { describe, expect, test } from "vitest";
import { buildRecordsCsv } from "./recordsCsv";
import type { TemperatureRecordFlatEntry } from "~/types/api";

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
