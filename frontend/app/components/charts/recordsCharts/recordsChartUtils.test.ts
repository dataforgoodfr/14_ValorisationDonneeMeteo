import { describe, it, expect } from "vitest";
import { countByPeriod, periodKey } from "./recordsChartUtils";

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
