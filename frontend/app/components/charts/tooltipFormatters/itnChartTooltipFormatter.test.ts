import { describe, it, expect } from "vitest";
import { itnChartTooltipFormatter } from "./itnChartTooltipFormatter";
import type { TooltipComponentFormatterCallbackParams } from "echarts";

const makeParam = (
    seriesName: string,
    value: Record<string, number | string>,
    marker = `<span style="color:black;">●</span>`,
) =>
    ({ seriesName, value, marker }) as unknown as NonNullable<
        Extract<TooltipComponentFormatterCallbackParams, unknown[]>[number]
    >;

const baseValue = {
    date: "2024-06-17",
    temperature: 22.5,
    baseline_mean: 20.0,
    baseline_min: 15.0,
    baseline_max: 28.0,
    baseline_std_dev_lower: 18.0,
    baseline_std_dev_upper: 22.0,
    isInterpolated: 0,
};

const makeDefaultParams = (overrides: Partial<typeof baseValue> = {}) => [
    makeParam("ITN", { ...baseValue, ...overrides }, `<span>T</span>`),
    makeParam(
        "ITN des normales",
        { ...baseValue, ...overrides },
        `<span>M</span>`,
    ),
    makeParam("Extrêmes", { ...baseValue, ...overrides }, `<span>E</span>`),
    makeParam("Écart-type", { ...baseValue, ...overrides }, `<span>S</span>`),
];

describe("itnChartTooltipFormatter", () => {
    // --- Guard cases ---

    it("returns empty string when params is not an array", () => {
        const result = itnChartTooltipFormatter(
            "not an array" as unknown as TooltipComponentFormatterCallbackParams,
            "day",
        );
        expect(result).toBe("");
    });

    it("returns empty string when params array is empty", () => {
        const result = itnChartTooltipFormatter([], "day");
        expect(result).toBe("");
    });

    it("returns empty string when isInterpolated is truthy", () => {
        const params = makeDefaultParams({ isInterpolated: 1 });
        const result = itnChartTooltipFormatter(params, "day");
        expect(result).toBe("");
    });

    it("returns content when isInterpolated is 0", () => {
        const params = makeDefaultParams({ isInterpolated: 0 });
        const result = itnChartTooltipFormatter(params, "day");
        expect(result).not.toBe("");
    });

    // --- Whole returned string ---

    it("returns the right string with granularity : day", () => {
        const params: TooltipComponentFormatterCallbackParams = [
            {
                componentType: "series",
                componentSubType: "line",
                componentIndex: 1,
                seriesName: "Extrêmes",
                name: "",
                dataIndex: 547,
                data: {
                    date: "2026-03-23",
                    temperature: 17.28,
                    baseline_mean: 18.48,
                    baseline_std_dev_upper: 20.11,
                    baseline_std_dev_lower: 16.86,
                    baseline_std_dev_band: 3.25,
                    baseline_max: 24.36,
                    baseline_min: 12.61,
                    baseline_band: 11.75,
                    cold_blue_band: 1.1999999999999993,
                    hot_red_band: 0,
                    hot_cold_invisible_band: 17.28,
                    isInterpolated: 0,
                },
                value: {
                    date: "2026-03-23",
                    temperature: 17.28,
                    baseline_mean: 18.48,
                    baseline_std_dev_upper: 20.11,
                    baseline_std_dev_lower: 16.86,
                    baseline_std_dev_band: 3.25,
                    baseline_max: 24.36,
                    baseline_min: 12.61,
                    baseline_band: 11.75,
                    cold_blue_band: 1.1999999999999993,
                    hot_red_band: 0,
                    hot_cold_invisible_band: 17.28,
                    isInterpolated: 0,
                },
                encode: {
                    x: [0],
                    y: [8],
                },
                $vars: ["seriesName", "name", "value"],
                marker: "dummy-marker",
            },
            {
                componentType: "series",
                componentSubType: "line",
                componentIndex: 3,
                seriesName: "Écart-type",
                name: "",
                dataIndex: 547,
                data: {
                    date: "2026-03-23",
                    temperature: 17.28,
                    baseline_mean: 18.48,
                    baseline_std_dev_upper: 20.11,
                    baseline_std_dev_lower: 16.86,
                    baseline_std_dev_band: 3.25,
                    baseline_max: 24.36,
                    baseline_min: 12.61,
                    baseline_band: 11.75,
                    cold_blue_band: 1.1999999999999993,
                    hot_red_band: 0,
                    hot_cold_invisible_band: 17.28,
                    isInterpolated: 0,
                },
                value: {
                    date: "2026-03-23",
                    temperature: 17.28,
                    baseline_mean: 18.48,
                    baseline_std_dev_upper: 20.11,
                    baseline_std_dev_lower: 16.86,
                    baseline_std_dev_band: 3.25,
                    baseline_max: 24.36,
                    baseline_min: 12.61,
                    baseline_band: 11.75,
                    cold_blue_band: 1.1999999999999993,
                    hot_red_band: 0,
                    hot_cold_invisible_band: 17.28,
                    isInterpolated: 0,
                },
                $vars: ["seriesName", "name", "value"],
                marker: 'dummy-marker"></span>',
            },
        ];
        const result = itnChartTooltipFormatter(params, "day");
        expect(result).toBe(
            'lun. 23 mars 2026<br/>ITN : 17.3°C<br/>ITN des normales : 18.5°C<br/>dummy-markerExtrêmes : [12.6°C – 24.4°C]<br/>dummy-marker"></span>Écart-type : [16.9°C – 20.1°C]',
        );
    });

    it("returns the right string with granularity : month", () => {
        const params: TooltipComponentFormatterCallbackParams = [
            {
                componentType: "series",
                componentSubType: "line",
                componentIndex: 1,
                seriesName: "Extrêmes",
                name: "",
                dataIndex: 17,
                data: {
                    date: "2026-03-01",
                    temperature: 17.99,
                    baseline_mean: 17.89,
                    baseline_std_dev_upper: 19.55,
                    baseline_std_dev_lower: 16.24,
                    baseline_std_dev_band: 3.3100000000000023,
                    baseline_max: 24.36,
                    baseline_min: 11.12,
                    baseline_band: 13.24,
                    cold_blue_band: 0,
                    hot_red_band: 0.09999999999999787,
                    hot_cold_invisible_band: 17.89,
                    isInterpolated: 0,
                },
                value: {
                    date: "2026-03-01",
                    temperature: 17.99,
                    baseline_mean: 17.89,
                    baseline_std_dev_upper: 19.55,
                    baseline_std_dev_lower: 16.24,
                    baseline_std_dev_band: 3.3100000000000023,
                    baseline_max: 24.36,
                    baseline_min: 11.12,
                    baseline_band: 13.24,
                    cold_blue_band: 0,
                    hot_red_band: 0.09999999999999787,
                    hot_cold_invisible_band: 17.89,
                    isInterpolated: 0,
                },
                $vars: ["seriesName", "name", "value"],
                marker: "dummy-marker",
            },
            {
                componentType: "series",
                componentSubType: "line",
                componentIndex: 3,
                seriesName: "Écart-type",
                name: "",
                dataIndex: 17,
                data: {
                    date: "2026-03-01",
                    temperature: 17.99,
                    baseline_mean: 17.89,
                    baseline_std_dev_upper: 19.55,
                    baseline_std_dev_lower: 16.24,
                    baseline_std_dev_band: 3.3100000000000023,
                    baseline_max: 24.36,
                    baseline_min: 11.12,
                    baseline_band: 13.24,
                    cold_blue_band: 0,
                    hot_red_band: 0.09999999999999787,
                    hot_cold_invisible_band: 17.89,
                    isInterpolated: 0,
                },
                value: {
                    date: "2026-03-01",
                    temperature: 17.99,
                    baseline_mean: 17.89,
                    baseline_std_dev_upper: 19.55,
                    baseline_std_dev_lower: 16.24,
                    baseline_std_dev_band: 3.3100000000000023,
                    baseline_max: 24.36,
                    baseline_min: 11.12,
                    baseline_band: 13.24,
                    cold_blue_band: 0,
                    hot_red_band: 0.09999999999999787,
                    hot_cold_invisible_band: 17.89,
                    isInterpolated: 0,
                },
                $vars: ["seriesName", "name", "value"],
                marker: 'dummy-marker"></span>',
            },
        ];
        const result = itnChartTooltipFormatter(params, "month");
        expect(result).toBe(
            'mars 2026<br/>ITN : 18.0°C<br/>ITN des normales : 17.9°C<br/>dummy-markerExtrêmes : [11.1°C – 24.4°C]<br/>dummy-marker"></span>Écart-type : [16.2°C – 19.6°C]',
        );
    });

    it("returns the right string with granularity : year", () => {
        const params: TooltipComponentFormatterCallbackParams = [
            {
                componentType: "series",
                componentSubType: "line",
                componentIndex: 1,
                seriesName: "Extrêmes",
                name: "",
                dataIndex: 1,
                data: {
                    date: "2026-01-01",
                    temperature: 15.49,
                    baseline_mean: 15.43,
                    baseline_std_dev_upper: 17.21,
                    baseline_std_dev_lower: 13.65,
                    baseline_std_dev_band: 3.5600000000000005,
                    baseline_max: 24.36,
                    baseline_min: 4.65,
                    baseline_band: 19.71,
                    cold_blue_band: 0,
                    hot_red_band: 0.0600000000000005,
                    hot_cold_invisible_band: 15.43,
                    isInterpolated: 0,
                },
                value: {
                    date: "2026-01-01",
                    temperature: 15.49,
                    baseline_mean: 15.43,
                    baseline_std_dev_upper: 17.21,
                    baseline_std_dev_lower: 13.65,
                    baseline_std_dev_band: 3.5600000000000005,
                    baseline_max: 24.36,
                    baseline_min: 4.65,
                    baseline_band: 19.71,
                    cold_blue_band: 0,
                    hot_red_band: 0.0600000000000005,
                    hot_cold_invisible_band: 15.43,
                    isInterpolated: 0,
                },
                $vars: ["seriesName", "name", "value"],
                marker: "dummy-marker",
            },
            {
                componentType: "series",
                componentSubType: "line",
                componentIndex: 3,
                seriesName: "Écart-type",
                name: "",
                dataIndex: 1,
                data: {
                    date: "2026-01-01",
                    temperature: 15.49,
                    baseline_mean: 15.43,
                    baseline_std_dev_upper: 17.21,
                    baseline_std_dev_lower: 13.65,
                    baseline_std_dev_band: 3.5600000000000005,
                    baseline_max: 24.36,
                    baseline_min: 4.65,
                    baseline_band: 19.71,
                    cold_blue_band: 0,
                    hot_red_band: 0.0600000000000005,
                    hot_cold_invisible_band: 15.43,
                    isInterpolated: 0,
                },
                value: {
                    date: "2026-01-01",
                    temperature: 15.49,
                    baseline_mean: 15.43,
                    baseline_std_dev_upper: 17.21,
                    baseline_std_dev_lower: 13.65,
                    baseline_std_dev_band: 3.5600000000000005,
                    baseline_max: 24.36,
                    baseline_min: 4.65,
                    baseline_band: 19.71,
                    cold_blue_band: 0,
                    hot_red_band: 0.0600000000000005,
                    hot_cold_invisible_band: 15.43,
                    isInterpolated: 0,
                },
                $vars: ["seriesName", "name", "value"],
                marker: 'dummy-marker"></span>',
            },
        ];
        const result = itnChartTooltipFormatter(params, "year");
        expect(result).toBe(
            '2026<br/>ITN : 15.5°C<br/>ITN des normales : 15.4°C<br/>dummy-markerExtrêmes : [4.7°C – 24.4°C]<br/>dummy-marker"></span>Écart-type : [13.7°C – 17.2°C]',
        );
    });

    // --- Date formatting by granularity ---

    it("formats date with month and year for 'month' granularity", () => {
        const params = makeDefaultParams({ date: "2024-06-15" });
        const result = itnChartTooltipFormatter(params, "month");

        expect(result).toContain("2024");
        expect(result).toContain("juin");
        expect(result).not.toMatch(
            /\blun\b|\bmar\b|\bmer\b|\bjeu\b|\bven\b|\bsam\b|\bdim\b/,
        );
    });

    it("formats date with year only for 'year' granularity", () => {
        const params = makeDefaultParams({ date: "2024-06-15" });
        const result = itnChartTooltipFormatter(params, "year");

        expect(result).toContain("2024");
        expect(result).not.toContain("juin");
    });

    it("formats date with weekday, day, month and year for 'day' granularity", () => {
        // 2024-06-17 is a Monday (lun. in French)
        const params = makeDefaultParams({ date: "2024-06-17" });
        const result = itnChartTooltipFormatter(params, "day");

        expect(result).toContain("2024");
        expect(result).toContain("juin");
        expect(result).toMatch(/lun\.|mar\.|mer\.|jeu\.|ven\.|sam\.|dim\./);
    });

    // --- Output structure ---

    it("joins 5 lines with <br/>", () => {
        const params = makeDefaultParams();
        const result = itnChartTooltipFormatter(params, "day");

        const parts = result.split("<br/>");
        expect(parts).toHaveLength(5);
    });

    it("first line is the formatted date", () => {
        const params = makeDefaultParams({ date: "2024-06-01" });
        const result = itnChartTooltipFormatter(params, "month");

        const parts = result.split("<br/>");
        expect(parts[0]).toContain("juin");
        expect(parts[0]).toContain("2024");
    });

    // --- Temperature line ---

    it("includes ITN with marker and formatted value", () => {
        const marker = `<span>T</span>`;
        const params = [
            makeParam("ITN", { ...baseValue, temperature: 22.5 }, marker),
            ...makeDefaultParams().slice(1),
        ];
        const result = itnChartTooltipFormatter(params, "day");

        expect(result).toContain(`${marker}ITN : 22.5°C`);
    });

    it("formats temperature with one decimal place", () => {
        const params = makeDefaultParams({ temperature: 20 });
        const result = itnChartTooltipFormatter(params, "day");

        expect(result).toContain("ITN : 20.0°C");
    });

    // --- ITN des normales line ---

    it("includes ITN des normales with marker and formatted value", () => {
        const marker = `<span>M</span>`;
        // All data is read from the first param's value, so override there
        const params = [
            makeParam(
                "ITN",
                { ...baseValue, baseline_mean: 19.3 },
                `<span>T</span>`,
            ),
            makeParam(
                "ITN des normales",
                { ...baseValue, baseline_mean: 19.3 },
                marker,
            ),
            makeParam("Extrêmes", { ...baseValue }, `<span>E</span>`),
            makeParam("Écart-type", { ...baseValue }, `<span>S</span>`),
        ];
        const result = itnChartTooltipFormatter(params, "day");

        expect(result).toContain(`${marker}ITN des normales : 19.3°C`);
    });

    it("formats baseline_mean with one decimal place", () => {
        const params = makeDefaultParams({ baseline_mean: 18 });
        const result = itnChartTooltipFormatter(params, "day");

        expect(result).toContain("ITN des normales : 18.0°C");
    });

    // --- Extrêmes line ---

    it("includes Extrêmes with marker and range", () => {
        const marker = `<span>E</span>`;
        const overrides = { baseline_min: 10.0, baseline_max: 30.0 };
        // All data is read from the first param's value, so override there
        const params = [
            makeParam("ITN", { ...baseValue, ...overrides }, `<span>T</span>`),
            makeParam("ITN des normales", { ...baseValue }, `<span>M</span>`),
            makeParam("Extrêmes", { ...baseValue, ...overrides }, marker),
            makeParam("Écart-type", { ...baseValue }, `<span>S</span>`),
        ];
        const result = itnChartTooltipFormatter(params, "day");

        expect(result).toContain(`${marker}Extrêmes : [10.0°C – 30.0°C]`);
    });

    it("formats extremes with one decimal place", () => {
        const params = makeDefaultParams({
            baseline_min: 12,
            baseline_max: 25,
        });
        const result = itnChartTooltipFormatter(params, "day");

        expect(result).toContain("Extrêmes : [12.0°C – 25.0°C]");
    });

    // --- Écart-type line ---

    it("includes Écart-type with marker and range", () => {
        const marker = `<span>S</span>`;
        const overrides = {
            baseline_std_dev_lower: 17.5,
            baseline_std_dev_upper: 23.5,
        };
        // All data is read from the first param's value, so override there
        const params = [
            makeParam("ITN", { ...baseValue, ...overrides }, `<span>T</span>`),
            makeParam("ITN des normales", { ...baseValue }, `<span>M</span>`),
            makeParam("Extrêmes", { ...baseValue }, `<span>E</span>`),
            makeParam("Écart-type", { ...baseValue, ...overrides }, marker),
        ];
        const result = itnChartTooltipFormatter(params, "day");

        expect(result).toContain(`${marker}Écart-type : [17.5°C – 23.5°C]`);
    });

    it("formats std dev bounds with one decimal place", () => {
        const params = makeDefaultParams({
            baseline_std_dev_lower: 16,
            baseline_std_dev_upper: 24,
        });
        const result = itnChartTooltipFormatter(params, "day");

        expect(result).toContain("Écart-type : [16.0°C – 24.0°C]");
    });

    // --- Missing marker ---

    it("falls back to empty string when series marker is absent", () => {
        const params = makeDefaultParams();
        (params[0] as unknown as Record<string, unknown>).marker = undefined;

        const result = itnChartTooltipFormatter(params, "day");

        // Output should still be produced; marker contribution is just empty
        expect(result).toContain("ITN :");
    });

    it("falls back to empty string when a series is not found in params", () => {
        // Only provide ITN — other series are absent
        const params = [makeParam("ITN", { ...baseValue })];
        const result = itnChartTooltipFormatter(params, "day");

        // Lines for missing series have no marker, output still rendered
        expect(result).toContain("ITN des normales :");
        expect(result).toContain("Extrêmes :");
        expect(result).toContain("Écart-type :");
    });
});
