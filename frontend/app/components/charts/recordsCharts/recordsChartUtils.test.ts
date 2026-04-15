import { describe, it, expect } from "vitest";
import { countByPeriod, niceMax, periodKey } from "./recordsChartUtils";

describe("niceMax", () => {
    it("arrondit au multiple de 1 pour les petites valeurs (step=1)", () => {
        // roughStep <= 1 → step=1 → ceil au multiple de 1
        expect(niceMax(3)).toBe(3);
        expect(niceMax(5)).toBe(5);
    });

    it("arrondit au multiple de 5 pour les valeurs moyennes (step=5)", () => {
        // roughStep in ]2, 5] → step=5
        expect(niceMax(17)).toBe(20);
        expect(niceMax(20)).toBe(20);
        expect(niceMax(21)).toBe(25);
    });

    it("arrondit au multiple de 20 pour les valeurs intermédiaires (step=20)", () => {
        // roughStep in ]10, 20] → step=20
        expect(niceMax(83)).toBe(100);
        expect(niceMax(100)).toBe(100);
    });

    it("arrondit au multiple de 50 au-delà de 100 (step=50)", () => {
        // roughStep in ]20, 50] → step=50
        expect(niceMax(101)).toBe(150);
    });

    it("arrondit au multiple de 200 pour les grandes valeurs (step=200)", () => {
        // roughStep in ]100, 200] → step=200
        expect(niceMax(850)).toBe(1000);
    });

    it("le résultat est toujours >= à la valeur d'entrée", () => {
        [1, 3, 7, 17, 43, 99, 250, 999].forEach((v) => {
            expect(niceMax(v)).toBeGreaterThanOrEqual(v);
        });
    });
});

describe("periodKey", () => {
    it("tronque à l'année avec granularité year", () => {
        expect(periodKey("2023-01-15", "year")).toBe("2023");
    });

    it("tronque au mois avec granularité month", () => {
        expect(periodKey("2023-01-15", "month")).toBe("2023-01");
    });

    it("conserve la date complète avec granularité day", () => {
        expect(periodKey("2023-01-15", "day")).toBe("2023-01-15");
    });
});

describe("countByPeriod", () => {
    it("regroupe par année avec granularité year", () => {
        const records = [
            { date: "2023-01-15" },
            { date: "2023-07-01" },
            { date: "2024-03-10" },
        ];

        expect(countByPeriod(records, "year")).toEqual({
            "2023": 2,
            "2024": 1,
        });
    });

    it("regroupe par mois avec granularité month", () => {
        const records = [
            { date: "2023-01-15" },
            { date: "2023-01-31" },
            { date: "2023-02-01" },
        ];

        expect(countByPeriod(records, "month")).toEqual({
            "2023-01": 2,
            "2023-02": 1,
        });
    });

    it("regroupe par jour avec granularité day", () => {
        const records = [
            { date: "2023-01-15" },
            { date: "2023-01-15" },
            { date: "2023-01-16" },
        ];

        expect(countByPeriod(records, "day")).toEqual({
            "2023-01-15": 2,
            "2023-01-16": 1,
        });
    });

    it("retourne un objet vide pour un tableau vide", () => {
        expect(countByPeriod([], "month")).toEqual({});
    });
});
