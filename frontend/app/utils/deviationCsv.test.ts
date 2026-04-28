import { describe, test, expect } from "vitest";
import { buildDeviationCsv } from "./deviationCsv";
import type { TemperatureDeviationStation } from "~/types/api";

const HEADERS =
    "Station,Département,Région,Écart à la normale (°C),Température Moyenne (°C)";

function makeStation(
    overrides: Partial<TemperatureDeviationStation> = {},
): TemperatureDeviationStation {
    return {
        station_id: "75001",
        station_name: "Paris",
        department: "Paris",
        region: "Île-de-France",
        deviation: 1.5,
        temperature_mean: 12.3,
        baseline_mean: 10.8,
        alt: 35,
        lat: 48.85,
        lon: 2.35,
        ...overrides,
    };
}

describe("buildDeviationCsv", () => {
    test("tableau vide — uniquement les en-têtes", () => {
        expect(buildDeviationCsv([])).toBe(`${HEADERS}\n`);
    });

    test("une station — ligne correcte", () => {
        const result = buildDeviationCsv([makeStation()]);
        expect(result).toBe(`${HEADERS}\nParis,Paris,Île-de-France,1.5,12.3`);
    });

    test("plusieurs stations — plusieurs lignes", () => {
        const result = buildDeviationCsv([
            makeStation({
                station_name: "Paris",
                deviation: 1.5,
                temperature_mean: 12.3,
            }),
            makeStation({
                station_name: "Lyon",
                department: "Rhône",
                region: "Auvergne-Rhône-Alpes",
                deviation: -0.3,
                temperature_mean: 11.1,
            }),
        ]);
        expect(result).toBe(
            `${HEADERS}\nParis,Paris,Île-de-France,1.5,12.3\nLyon,Rhône,Auvergne-Rhône-Alpes,-0.3,11.1`,
        );
    });

    test("nom de station avec virgule — encapsulé", () => {
        const result = buildDeviationCsv([
            makeStation({ station_name: "Paris, 7e" }),
        ]);
        expect(result).toBe(
            `${HEADERS}\n"Paris, 7e",Paris,Île-de-France,1.5,12.3`,
        );
    });
});
