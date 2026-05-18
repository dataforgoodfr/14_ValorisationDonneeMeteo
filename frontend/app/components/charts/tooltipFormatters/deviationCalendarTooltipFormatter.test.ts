import { describe, expect, it } from "vitest";
import { deviationCalendarTooltipFormatter } from "./deviationCalendarTooltipFormatter";
import type { DefaultLabelFormatterCallbackParams } from "echarts";

const categories = {
    xAxis: ["2023", "2024", "2025"],
    yAxis: ["jan", "fév", "mar"],
};

const makeParam = (
    overrides: Partial<DefaultLabelFormatterCallbackParams>,
): DefaultLabelFormatterCallbackParams => ({
    componentType: "series",
    componentSubType: "heatmap",
    componentIndex: 0,
    seriesType: "heatmap",
    seriesIndex: 0,
    seriesName: "Station A",
    name: "",
    dataIndex: 0,
    data: [0, 0, 1.0],
    value: [0, 0, 1.0],
    $vars: [],
    ...overrides,
});

describe("deviationCalendarTooltipFormatter", () => {
    describe("Mode non-vertical (défaut)", () => {
        it("retourne '' si params n'a pas de propriété data", () => {
            const result = deviationCalendarTooltipFormatter(
                {} as DefaultLabelFormatterCallbackParams,
                "year",
                categories,
            );
            expect(result).toBe("");
        });

        it("retourne '' si params.data n'est pas un tableau", () => {
            const result = deviationCalendarTooltipFormatter(
                {
                    data: "invalid",
                } as unknown as DefaultLabelFormatterCallbackParams,
                "year",
                categories,
            );
            expect(result).toBe("");
        });

        it("affiche xLabel · yLabel pour granularité year", () => {
            const result = deviationCalendarTooltipFormatter(
                makeParam({ data: [1, 2, 2.5] }),
                "year",
                categories,
            );
            expect(result).toContain("2024 · mar");
        });

        it("affiche yLabel/xLabel pour granularité day", () => {
            const result = deviationCalendarTooltipFormatter(
                makeParam({ data: [0, 1, -1.0] }),
                "day",
                categories,
            );
            expect(result).toContain("fév/2023");
        });

        it("affiche le signe + pour valeur positive", () => {
            const result = deviationCalendarTooltipFormatter(
                makeParam({ data: [0, 0, 3.2] }),
                "year",
                categories,
            );
            expect(result).toContain("+3.2");
        });

        it("n'affiche pas de signe + pour valeur négative", () => {
            const result = deviationCalendarTooltipFormatter(
                makeParam({ data: [0, 0, -1.5] }),
                "year",
                categories,
            );
            expect(result).toContain("-1.5");
            expect(result).not.toContain("+-");
        });

        it("utilise la couleur hot pour valeur positive", () => {
            const result = deviationCalendarTooltipFormatter(
                makeParam({ data: [0, 0, 1.0] }),
                "year",
                categories,
            );
            expect(result).toContain("#d32F2F");
        });

        it("utilise la couleur cold pour valeur négative", () => {
            const result = deviationCalendarTooltipFormatter(
                makeParam({ data: [0, 0, -1.0] }),
                "year",
                categories,
            );
            expect(result).toContain("#1976D2");
        });

        it("affiche le nom de la série", () => {
            const result = deviationCalendarTooltipFormatter(
                makeParam({ seriesName: "Lyon", data: [0, 0, 1.0] }),
                "year",
                categories,
            );
            expect(result).toContain("Lyon");
        });
    });

    describe("Mode vertical (nouveau cas)", () => {
        it("retourne '' si le tableau de params est vide", () => {
            const result = deviationCalendarTooltipFormatter(
                [],
                "year",
                categories,
                true,
            );
            expect(result).toBe("");
        });

        it("retourne '' si le premier item n'a pas de data tableau", () => {
            const result = deviationCalendarTooltipFormatter(
                [makeParam({ data: undefined as unknown as [] })],
                "year",
                categories,
                true,
            );
            expect(result).toBe("");
        });

        it("affiche le xLabel issu de categories.xAxis", () => {
            const result = deviationCalendarTooltipFormatter(
                [makeParam({ data: [2, 0, 1.0] })],
                "year",
                categories,
                true,
            );
            expect(result).toContain("2025");
        });

        it("affiche le seriesName en gras", () => {
            const result = deviationCalendarTooltipFormatter(
                [makeParam({ seriesName: "Lyon", data: [0, 0, 1.0] })],
                "year",
                categories,
                true,
            );
            expect(result).toContain('<b style="color:#000">Lyon</b>');
        });

        it("affiche le signe + pour valeur positive", () => {
            const result = deviationCalendarTooltipFormatter(
                [makeParam({ data: [0, 0, 2.4] })],
                "year",
                categories,
                true,
            );
            expect(result).toContain("+2.4");
        });

        it("n'affiche pas de signe + pour valeur négative", () => {
            const result = deviationCalendarTooltipFormatter(
                [makeParam({ data: [0, 0, -3.1] })],
                "year",
                categories,
                true,
            );
            expect(result).toContain("-3.1");
            expect(result).not.toContain("+-");
        });

        it("utilise la couleur hot pour valeur positive", () => {
            const result = deviationCalendarTooltipFormatter(
                [makeParam({ data: [0, 0, 1.0] })],
                "year",
                categories,
                true,
            );
            expect(result).toContain("#d32F2F");
        });

        it("utilise la couleur cold pour valeur négative", () => {
            const result = deviationCalendarTooltipFormatter(
                [makeParam({ data: [0, 0, -1.0] })],
                "year",
                categories,
                true,
            );
            expect(result).toContain("#1976D2");
        });

        it("joint plusieurs séries avec <br/><br/>", () => {
            const params = [
                makeParam({
                    seriesIndex: 0,
                    seriesName: "Lyon",
                    data: [0, 0, 1.5],
                }),
                makeParam({
                    seriesIndex: 1,
                    seriesName: "Paris",
                    data: [0, 1, -0.8],
                }),
            ];
            const result = deviationCalendarTooltipFormatter(
                params,
                "year",
                categories,
                true,
            );
            expect(result).toContain("Lyon");
            expect(result).toContain("Paris");
            expect(result).toContain("<br/><br/>");
        });

        it("déduplique les entrées ayant le même seriesIndex", () => {
            const params = [
                makeParam({
                    seriesIndex: 0,
                    seriesName: "Lyon",
                    data: [0, 0, 1.5],
                }),
                makeParam({
                    seriesIndex: 0,
                    seriesName: "Lyon",
                    data: [0, 1, 1.5],
                }),
                makeParam({
                    seriesIndex: 1,
                    seriesName: "Paris",
                    data: [0, 0, -0.5],
                }),
            ];
            const result = deviationCalendarTooltipFormatter(
                params,
                "year",
                categories,
                true,
            );
            const lyonOccurrences = (result.match(/Lyon/g) ?? []).length;
            expect(lyonOccurrences).toBe(1);
            expect(result).toContain("Paris");
        });

        it("fonctionne quand params est un objet unique (non-tableau)", () => {
            const result = deviationCalendarTooltipFormatter(
                makeParam({ data: [1, 0, 0.7] }),
                "year",
                categories,
                true,
            );
            expect(result).toContain("2024");
            expect(result).toContain("+0.7");
        });
    });
});
