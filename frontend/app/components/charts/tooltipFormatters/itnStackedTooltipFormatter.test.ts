import { describe, it, expect } from "vitest";
import {
    formatStackedPosition,
    formatStackedAxisLabel,
    formatContinuousAxisLabel,
} from "./itnStackedTooltipFormatter";

describe("formatStackedPosition", () => {
    describe("granularity: month", () => {
        it("retourne le nom du mois capitalisé pour janvier", () => {
            expect(formatStackedPosition("01", "month")).toBe("Janvier");
        });

        it("retourne le nom du mois capitalisé pour mars", () => {
            expect(formatStackedPosition("03", "month")).toBe("Mars");
        });

        it("retourne le nom du mois capitalisé pour décembre", () => {
            expect(formatStackedPosition("12", "month")).toBe("Décembre");
        });
    });

    describe("granularity: day", () => {
        it("retourne le jour et le mois en français pour le 1er janvier", () => {
            expect(formatStackedPosition("01-01", "day")).toBe("1 janvier");
        });

        it("retourne le jour et le mois en français pour le 15 mars", () => {
            expect(formatStackedPosition("03-15", "day")).toBe("15 mars");
        });

        it("retourne le jour et le mois en français pour le 31 décembre", () => {
            expect(formatStackedPosition("12-31", "day")).toBe("31 décembre");
        });
    });
});

describe("formatStackedAxisLabel", () => {
    describe("granularity: month", () => {
        it("retourne l'abréviation du mois pour janvier", () => {
            expect(formatStackedAxisLabel("01", "month")).toBe("Janv.");
        });

        it("retourne l'abréviation du mois pour mars", () => {
            expect(formatStackedAxisLabel("03", "month")).toBe("Mars");
        });

        it("retourne l'abréviation du mois pour décembre", () => {
            expect(formatStackedAxisLabel("12", "month")).toBe("Déc.");
        });
    });

    describe("granularity: day", () => {
        it("retourne 01-Janv. pour le 1er janvier", () => {
            expect(formatStackedAxisLabel("01-01", "day")).toBe("01-Janv.");
        });

        it("retourne 01-Mars pour n'importe quel jour de mars", () => {
            expect(formatStackedAxisLabel("03-15", "day")).toBe("01-Mars");
        });

        it("retourne 01-Déc. pour n'importe quel jour de décembre", () => {
            expect(formatStackedAxisLabel("12-31", "day")).toBe("01-Déc.");
        });
    });
});

describe("formatContinuousAxisLabel", () => {
    it("retourne DD-Janv. pour le 1er janvier", () => {
        expect(formatContinuousAxisLabel(new Date(2024, 0, 1).getTime())).toBe(
            "01-Janv.",
        );
    });

    it("retourne DD-Mars pour le 15 mars", () => {
        expect(formatContinuousAxisLabel(new Date(2024, 2, 15).getTime())).toBe(
            "15-Mars",
        );
    });

    it("retourne DD-Déc. pour le 31 décembre", () => {
        expect(
            formatContinuousAxisLabel(new Date(2024, 11, 31).getTime()),
        ).toBe("31-Déc.");
    });
});
