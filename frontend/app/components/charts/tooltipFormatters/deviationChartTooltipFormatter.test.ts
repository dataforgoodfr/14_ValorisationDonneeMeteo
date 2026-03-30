import { describe, it, expect } from "vitest";
import { deviationChartTooltipFormatter } from "./deviationChartTooltipFormatter";
import type { TooltipComponentFormatterCallbackParams } from "echarts";

const makeParam = (
    seriesName: string,
    value: Record<string, number | string>,
    marker = `<span style="color:red;">●</span>`,
) =>
    ({ seriesName, value, marker }) as unknown as NonNullable<
        Extract<TooltipComponentFormatterCallbackParams, unknown[]>[number]
    >;

describe("deviationChartTooltipFormatter", () => {
    // --- Guard cases ---

    it("returns empty string when params is not an array", () => {
        const result = deviationChartTooltipFormatter(
            "not an array" as unknown as TooltipComponentFormatterCallbackParams,
            "day",
        );
        expect(result).toBe("");
    });

    it("returns empty string when params array is empty", () => {
        const result = deviationChartTooltipFormatter([], "day");
        expect(result).toBe("");
    });

    // --- Whole returned string ---

    it("returns the right string with granularity : day", () => {
        const params: TooltipComponentFormatterCallbackParams = [
            {
                componentType: "series",
                componentSubType: "bar",
                componentIndex: 0,
                seriesName: "Ecart positif",
                name: "",
                dataIndex: 2,
                data: {
                    date: "2025-03-02",
                    deviation: -0.4,
                    deviation_positive: null,
                    deviation_negative: -0.4,
                },
                value: {
                    date: "2025-03-02",
                    deviation: -0.4,
                    deviation_positive: null,
                    deviation_negative: -0.4,
                },
                $vars: ["seriesName", "name", "value"],
                marker: "marker-positif",
            },
            {
                componentType: "series",
                componentSubType: "bar",
                componentIndex: 1,
                seriesName: "Ecart négatif",
                name: "",
                dataIndex: 2,
                data: {
                    date: "2025-03-02",
                    deviation: -0.4,
                    deviation_positive: null,
                    deviation_negative: -0.4,
                },
                value: {
                    date: "2025-03-02",
                    deviation: -0.4,
                    deviation_positive: null,
                    deviation_negative: -0.4,
                },
                $vars: ["seriesName", "name", "value"],
                marker: "marker-negatif",
            },
        ];
        const result = deviationChartTooltipFormatter(params, "day");
        expect(result).toBe("dim. 2 mars 2025<br/>marker-negatif : -0.4°C");
    });

    it("returns the right string with granularity : month", () => {
        const params: TooltipComponentFormatterCallbackParams = [
            {
                componentType: "series",
                componentSubType: "bar",
                componentIndex: 0,
                seriesName: "Ecart positif",
                name: "",
                dataIndex: 12,
                data: {
                    date: "2026-03-01",
                    deviation: 0.1,
                    deviation_positive: 0.1,
                    deviation_negative: null,
                },
                value: {
                    date: "2026-03-01",
                    deviation: 0.1,
                    deviation_positive: 0.1,
                    deviation_negative: null,
                },
                $vars: ["seriesName", "name", "value"],
                marker: "marker-positif",
            },
            {
                componentType: "series",
                componentSubType: "bar",
                componentIndex: 1,
                seriesType: "bar",
                seriesName: "Ecart négatif",
                name: "",
                dataIndex: 12,
                data: {
                    date: "2026-03-01",
                    deviation: 0.1,
                    deviation_positive: 0.1,
                    deviation_negative: null,
                },
                value: {
                    date: "2026-03-01",
                    deviation: 0.1,
                    deviation_positive: 0.1,
                    deviation_negative: null,
                },
                $vars: ["seriesName", "name", "value"],
                marker: "marker-negatif",
            },
        ];
        const result = deviationChartTooltipFormatter(params, "month");
        expect(result).toBe("mars 2026<br/>marker-positif : +0.1°C");
    });

    it("returns the right string with granularity : year", () => {
        const params: TooltipComponentFormatterCallbackParams = [
            {
                componentType: "series",
                componentSubType: "bar",
                componentIndex: 0,
                seriesType: "bar",
                seriesName: "Ecart positif",
                name: "",
                dataIndex: 1,
                data: {
                    date: "2026-01-01",
                    deviation: 0.04,
                    deviation_positive: 0.04,
                    deviation_negative: null,
                },
                value: {
                    date: "2026-01-01",
                    deviation: 0.04,
                    deviation_positive: 0.04,
                    deviation_negative: null,
                },
                $vars: ["seriesName", "name", "value"],
                marker: "marker-positif",
            },
            {
                componentType: "series",
                componentSubType: "bar",
                componentIndex: 1,
                seriesType: "bar",
                seriesName: "Ecart négatif",
                name: "",
                dataIndex: 1,
                data: {
                    date: "2026-01-01",
                    deviation: 0.04,
                    deviation_positive: 0.04,
                    deviation_negative: null,
                },
                value: {
                    date: "2026-01-01",
                    deviation: 0.04,
                    deviation_positive: 0.04,
                    deviation_negative: null,
                },
                $vars: ["seriesName", "name", "value"],
                marker: "marker-negatif",
            },
        ];
        const result = deviationChartTooltipFormatter(params, "year");
        expect(result).toBe("2026<br/>marker-positif : +0.0°C");
    });

    // --- Date formatting by granularity ---

    it("formats date with month and year for 'month' granularity", () => {
        const params = [
            makeParam("Ecart positif", {
                date: "2024-06-15",
                deviation_positive: 1.5,
            }),
        ];

        const result = deviationChartTooltipFormatter(params, "month");

        // French locale: "juin 2024"
        expect(result).toContain("2024");
        expect(result).toContain("juin");
        // Should NOT contain weekday or short day number (day-level detail)
        expect(result).not.toMatch(
            /\blun\b|\bmar\b|\bmer\b|\bjeu\b|\bven\b|\bsam\b|\bdim\b/,
        );
    });

    it("formats date with year only for 'year' granularity", () => {
        const params = [
            makeParam("Ecart positif", {
                date: "2024-06-15",
                deviation_positive: 2.0,
            }),
        ];

        const result = deviationChartTooltipFormatter(params, "year");

        expect(result).toContain("2024");
        expect(result).not.toContain("juin");
    });

    it("formats date with weekday, day, month and year for 'day' granularity", () => {
        // 2024-06-17 is a Monday (lun. in French)
        const params = [
            makeParam("Ecart positif", {
                date: "2024-06-17",
                deviation_positive: 0.8,
            }),
        ];

        const result = deviationChartTooltipFormatter(params, "day");

        expect(result).toContain("2024");
        expect(result).toContain("juin");
        // Should include a weekday abbreviation
        expect(result).toMatch(/lun\.|mar\.|mer\.|jeu\.|ven\.|sam\.|dim\./);
    });

    // --- Positive deviation ---

    it("uses 'Ecart positif' series and '+' sign for positive deviation", () => {
        const marker = `<span>▲</span>`;
        const params = [
            makeParam(
                "Ecart positif",
                { date: "2024-01-01", deviation_positive: 3.7 },
                marker,
            ),
            makeParam("Ecart négatif", {
                date: "2024-01-01",
                deviation_negative: 0,
            }),
        ];

        const result = deviationChartTooltipFormatter(params, "month");

        expect(result).toContain(marker);
        expect(result).toContain("+3.7°C");
    });

    it("formats positive deviation with one decimal place", () => {
        const params = [
            makeParam("Ecart positif", {
                date: "2024-01-01",
                deviation_positive: 3,
            }),
        ];

        const result = deviationChartTooltipFormatter(params, "month");

        expect(result).toContain("+3.0°C");
    });

    // --- Negative deviation ---

    it("uses 'Ecart négatif' series and no '+' sign for negative deviation", () => {
        const marker = `<span>▼</span>`;
        // Only deviation_negative is set: deviation_positive is absent so ?? falls through
        const params = [
            makeParam(
                "Ecart négatif",
                { date: "2024-01-01", deviation_negative: -2.3 },
                marker,
            ),
        ];

        const result = deviationChartTooltipFormatter(params, "month");

        expect(result).toContain(marker);
        expect(result).toContain("-2.3°C");
        expect(result).not.toContain("+-2.3°C");
    });

    it("formats negative deviation with one decimal place", () => {
        const params = [
            makeParam("Ecart négatif", {
                date: "2024-01-01",
                deviation_negative: -1,
            }),
        ];

        const result = deviationChartTooltipFormatter(params, "month");

        expect(result).toContain("-1.0°C");
    });

    // --- Zero deviation ---

    it("treats zero deviation as positive (uses '+' sign and 'Ecart positif' series)", () => {
        const marker = `<span>◆</span>`;
        const params = [
            makeParam(
                "Ecart positif",
                { date: "2024-01-01", deviation_positive: 0 },
                marker,
            ),
        ];

        const result = deviationChartTooltipFormatter(params, "month");

        expect(result).toContain("+0.0°C");
        expect(result).toContain(marker);
    });

    // --- Missing marker ---

    it("falls back to empty string when matching series has no marker", () => {
        const params = [
            makeParam(
                "Ecart positif",
                { date: "2024-01-01", deviation_positive: 1.0 },
                undefined as unknown as string,
            ),
        ];

        // Override marker to undefined
        (params[0] as unknown as Record<string, unknown>).marker = undefined;

        const result = deviationChartTooltipFormatter(params, "month");

        // Should still produce output, marker part is just empty
        expect(result).toContain("+1.0°C");
        expect(result).toContain(" : ");
    });

    // --- Output structure ---

    it("joins date and value lines with <br/>", () => {
        const params = [
            makeParam("Ecart positif", {
                date: "2024-06-01",
                deviation_positive: 1.2,
            }),
        ];

        const result = deviationChartTooltipFormatter(params, "month");

        const parts = result.split("<br/>");
        expect(parts).toHaveLength(2);
        expect(parts[0]).toContain("2024");
        expect(parts[1]).toContain("1.2°C");
    });
});
