import { describe, expect, test } from "vitest";
import { buildItnCsv } from "./itnCsv";
import type { NationalIndicatorDataPoint } from "~/types/api";

function makeItnPoint(
    overrides: Partial<NationalIndicatorDataPoint> = {},
): NationalIndicatorDataPoint {
    return {
        date: "2023-07-14",
        temperature: 42.0,
        baseline_mean: 25.0,
        baseline_std_dev_lower: 18.0,
        baseline_std_dev_upper: 32.0,
        baseline_max: 40.0,
        baseline_min: 10.0,
        is_hot_peak: true,
        is_cold_peak: false,
        ...overrides,
    };
}

const HEADERS = "Date,ITN (°C),ITN_baseline_mean (°C)";

describe("buildItnCsv", () => {
    describe("hot type", () => {
        test("empty array returns only headers", () => {
            const result = buildItnCsv([], "hot");
            expect(result).toBe(`${HEADERS}\n`);
        });

        test("one row with temperature > baseline_std_dev_upper is included", () => {
            const result = buildItnCsv(
                [makeItnPoint({ temperature: 35.0 })],
                "hot",
            );
            expect(result).toBe(`${HEADERS}\n2023-07-14,35,25`);
        });

        test("one row with temperature <= baseline_std_dev_upper is excluded", () => {
            const result = buildItnCsv(
                [makeItnPoint({ temperature: 30.0 })],
                "hot",
            );
            expect(result).toBe(`${HEADERS}\n`);
        });

        test("multiple hot points filtered correctly", () => {
            const result = buildItnCsv(
                [
                    makeItnPoint({
                        temperature: 40.0,
                        date: "2023-07-14",
                    }),
                    makeItnPoint({
                        temperature: 28.0,
                        date: "2023-07-15",
                    }),
                    makeItnPoint({
                        temperature: 38.5,
                        date: "2023-07-16",
                    }),
                ],
                "hot",
            );
            const lines = result.split("\n");
            expect(lines).toHaveLength(3);
            expect(lines[1]).toBe("2023-07-14,40,25");
            expect(lines[2]).toBe("2023-07-16,38.5,25");
        });

        test("edge case: temperature exactly equal to baseline_std_dev_upper is excluded", () => {
            const result = buildItnCsv(
                [makeItnPoint({ temperature: 32.0 })],
                "hot",
            );
            expect(result).toBe(`${HEADERS}\n`);
        });

        test("complete case - multiple points with hot filtering", () => {
            const result = buildItnCsv(
                [
                    makeItnPoint({
                        date: "2023-06-15",
                        temperature: 42.5,
                        baseline_mean: 24.0,
                    }),
                    makeItnPoint({
                        date: "2023-06-20",
                        temperature: 41.0,
                        baseline_mean: 24.5,
                    }),
                    makeItnPoint({
                        date: "2023-07-10",
                        temperature: 28.0,
                        baseline_mean: 26.0,
                    }),
                ],
                "hot",
            );
            expect(result).toBe(
                "Date,ITN (°C),ITN_baseline_mean (°C)\n" +
                    "2023-06-15,42.5,24\n" +
                    "2023-06-20,41,24.5",
            );
        });
    });

    describe("cold type", () => {
        test("empty array returns only headers", () => {
            const result = buildItnCsv([], "cold");
            expect(result).toBe(`${HEADERS}\n`);
        });

        test("one row with temperature < baseline_std_dev_lower is included", () => {
            const result = buildItnCsv(
                [makeItnPoint({ temperature: 15.0 })],
                "cold",
            );
            expect(result).toBe(`${HEADERS}\n2023-07-14,15,25`);
        });

        test("one row with temperature >= baseline_std_dev_lower is excluded", () => {
            const result = buildItnCsv(
                [makeItnPoint({ temperature: 20.0 })],
                "cold",
            );
            expect(result).toBe(`${HEADERS}\n`);
        });

        test("multiple cold points filtered correctly", () => {
            const result = buildItnCsv(
                [
                    makeItnPoint({
                        temperature: 10.0,
                        date: "2023-01-14",
                    }),
                    makeItnPoint({
                        temperature: 25.0,
                        date: "2023-01-15",
                    }),
                    makeItnPoint({
                        temperature: 5.0,
                        date: "2023-01-16",
                    }),
                ],
                "cold",
            );
            const lines = result.split("\n");
            expect(lines).toHaveLength(3);
            expect(lines[1]).toBe("2023-01-14,10,25");
            expect(lines[2]).toBe("2023-01-16,5,25");
        });

        test("edge case: temperature exactly equal to baseline_std_dev_lower is excluded", () => {
            const result = buildItnCsv(
                [makeItnPoint({ temperature: 18.0 })],
                "cold",
            );
            expect(result).toBe(`${HEADERS}\n`);
        });

        test("complete case - multiple points with cold filtering", () => {
            const result = buildItnCsv(
                [
                    makeItnPoint({
                        date: "2023-01-05",
                        temperature: 5.0,
                        baseline_mean: 8.0,
                    }),
                    makeItnPoint({
                        date: "2023-01-10",
                        temperature: -3.0,
                        baseline_mean: 7.5,
                    }),
                    makeItnPoint({
                        date: "2023-01-15",
                        temperature: 19.0,
                        baseline_mean: 8.5,
                    }),
                ],
                "cold",
            );
            expect(result).toBe(
                "Date,ITN (°C),ITN_baseline_mean (°C)\n" +
                    "2023-01-05,5,8\n" +
                    "2023-01-10,-3,7.5",
            );
        });
    });

    describe("filtering behavior with hot and cold", () => {
        test("same data, different filtering based on hot vs cold type", () => {
            const data = [
                makeItnPoint({
                    date: "2023-07-01",
                    temperature: 35.0,
                }),
                makeItnPoint({
                    date: "2023-01-01",
                    temperature: 10.0,
                }),
            ];
            const hotCsv = buildItnCsv(data, "hot");
            const coldCsv = buildItnCsv(data, "cold");

            expect(hotCsv).toContain("2023-07-01");
            expect(hotCsv).not.toContain("2023-01-01");

            expect(coldCsv).toContain("2023-01-01");
            expect(coldCsv).not.toContain("2023-07-01");
        });
    });

    describe("decimal value preservation", () => {
        test("decimal values are preserved", () => {
            const result = buildItnCsv(
                [
                    makeItnPoint({
                        temperature: 42.7,
                        baseline_mean: 25.3,
                    }),
                ],
                "hot",
            );
            expect(result).toContain("42.7,25.3");
        });

        test("negative values for cold are preserved", () => {
            const result = buildItnCsv(
                [
                    makeItnPoint({
                        temperature: -5.2,
                        baseline_mean: 8.1,
                    }),
                ],
                "cold",
            );
            expect(result).toContain("-5.2,8.1");
        });
    });
});
