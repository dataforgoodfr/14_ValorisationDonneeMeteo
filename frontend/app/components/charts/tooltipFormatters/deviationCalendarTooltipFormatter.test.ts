import { describe, expect, it } from "vitest";
import { deviationCalendarTooltipFormatter } from "./deviationCalendarTooltipFormatter";
import type { DefaultLabelFormatterCallbackParams } from "echarts";

const categories = {
    xAxis: ["2023", "2024", "2025"],
    yAxis: ["jan", "fév", "mar"],
};

function makeParam(
    overrides: Partial<DefaultLabelFormatterCallbackParams>,
): DefaultLabelFormatterCallbackParams {
    return {
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
    };
}

describe("deviationCalendarTooltipFormatter", () => {
    describe("Whole returned string", () => {
        it("retourne la chaîne complète pour granularité year", () => {
            const result = deviationCalendarTooltipFormatter(
                makeParam({ seriesName: "Station A", data: [1, 2, 2.5] }),
                "year",
                categories,
            );
            expect(result).toBe(
                '<b style="color:#000">Station A</b><br/>' +
                    '<span style="color:#aaa">2024 · mar</span><br/>' +
                    '<span style="color:#d32F2F">● +2.5 °C</span>',
            );
        });

        it("retourne la chaîne complète pour granularité day", () => {
            const result = deviationCalendarTooltipFormatter(
                makeParam({ seriesName: "Station A", data: [0, 1, -1.0] }),
                "day",
                categories,
            );
            expect(result).toBe(
                '<b style="color:#000">Station A</b><br/>' +
                    '<span style="color:#aaa">fév/2023</span><br/>' +
                    '<span style="color:#1976D2">● -1.0 °C</span>',
            );
        });

        it("retourne la chaîne complète en mode vertical pour plusieurs séries", () => {
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
            expect(result).toBe(
                '<b style="color:#000">Lyon</b><br/>' +
                    '<span style="color:#aaa">2023</span><br/>' +
                    '<span style="color:#d32F2F">● +1.5 °C</span>' +
                    "<br/><br/>" +
                    '<b style="color:#000">Paris</b><br/>' +
                    '<span style="color:#aaa">2023</span><br/>' +
                    '<span style="color:#1976D2">● -0.8 °C</span>',
            );
        });
    });

    describe("Mode non-vertical (défaut)", () => {
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
