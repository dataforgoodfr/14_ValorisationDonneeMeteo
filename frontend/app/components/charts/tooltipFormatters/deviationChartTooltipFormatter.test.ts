import { describe, expect, it } from "vitest";
import { deviationChartTooltipFormatter } from "./deviationChartTooltipFormatter";
import type { DefaultLabelFormatterCallbackParams } from "echarts";

const makeParam = (
    seriesName: string,
    value: Record<string, number | string>,
    marker = `<span style="color:red;">●</span>`,
): DefaultLabelFormatterCallbackParams => ({
    componentType: "series",
    componentSubType: "bar",
    componentIndex: 0,
    seriesName,
    name: "",
    dataIndex: 0,
    data: value,
    value,
    marker,
    $vars: ["seriesName", "name", "value"],
});

describe("deviationChartTooltipFormatter", () => {
    // --- Guard cases ---

    it("returns empty string when params is not an array", () => {
        const result = deviationChartTooltipFormatter(
            makeParam("", {}),
            "day",
            [],
        );
        expect(result).toBe("");
    });

    it("returns empty string when params array is empty", () => {
        const result = deviationChartTooltipFormatter([], "day", []);
        expect(result).toBe("");
    });

    // --- Whole returned string ---

    it("returns the right string with granularity : day", () => {
        const params: DefaultLabelFormatterCallbackParams[] = [
            {
                componentType: "series",
                componentSubType: "bar",
                componentIndex: 0,
                seriesIndex: 0,
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
                seriesIndex: 0,
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
        const result = deviationChartTooltipFormatter(params, "day", ["Lyon"]);
        expect(result).toBe(
            "dim. 2 mars 2025<br/>marker-negatif Lyon : -0.4°C",
        );
    });

    it("returns the right string with granularity : month", () => {
        const params: DefaultLabelFormatterCallbackParams[] = [
            {
                componentType: "series",
                componentSubType: "bar",
                componentIndex: 0,
                seriesIndex: 0,
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
                seriesIndex: 0,
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
        const result = deviationChartTooltipFormatter(params, "month", [
            "Lyon",
        ]);
        expect(result).toBe("mars 2026<br/>marker-positif Lyon : +0.1°C");
    });

    it("returns the right string with granularity : year", () => {
        const params: DefaultLabelFormatterCallbackParams[] = [
            {
                componentType: "series",
                componentSubType: "bar",
                componentIndex: 0,
                seriesType: "bar",
                seriesIndex: 0,
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
                seriesIndex: 0,
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
        const result = deviationChartTooltipFormatter(params, "year", ["Lyon"]);
        expect(result).toBe("2026<br/>marker-positif Lyon : +0.0°C");
    });

    // --- Date formatting by granularity ---

    it("formats date with month and year for 'month' granularity", () => {
        const params = [
            makeParam("Ecart positif", {
                date: "2024-06-15",
                deviation_positive: 1.5,
            }),
        ];

        const result = deviationChartTooltipFormatter(params, "month", [
            "Station",
        ]);

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

        const result = deviationChartTooltipFormatter(params, "year", [
            "Station",
        ]);

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

        const result = deviationChartTooltipFormatter(params, "day", [
            "Station",
        ]);

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

        const result = deviationChartTooltipFormatter(params, "month", [
            "Station",
        ]);

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

        const result = deviationChartTooltipFormatter(params, "month", [
            "Station",
        ]);

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

        const result = deviationChartTooltipFormatter(params, "month", [
            "Station",
        ]);

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

        const result = deviationChartTooltipFormatter(params, "month", [
            "Station",
        ]);

        expect(result).toContain("-1.0°C");
    });

    // --- Zero deviation ---

    it("treats zero deviation as neutral (no sign, 'Ecart positif' series)", () => {
        const marker = `<span>◆</span>`;
        const params = [
            makeParam(
                "Ecart positif",
                { date: "2024-01-01", deviation_positive: 0 },
                marker,
            ),
        ];

        const result = deviationChartTooltipFormatter(params, "month", [
            "Station",
        ]);

        expect(result).toContain("0.0°C");
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

        const result = deviationChartTooltipFormatter(params, "month", [
            "Station",
        ]);

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

        const result = deviationChartTooltipFormatter(params, "month", [
            "Station",
        ]);

        const parts = result.split("<br/>");
        expect(parts).toHaveLength(2);
        expect(parts[0]).toContain("2024");
        expect(parts[1]).toContain("1.2°C");
    });
});
