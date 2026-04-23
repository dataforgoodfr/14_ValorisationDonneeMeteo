import { beforeAll, describe, expect, it } from "vitest";
import { fetchNationalIndicatorForYear } from "./nationalIndicatorFetcher.real";

import type { GranularityType } from "~/components/ui/commons/selectBar/types";
import type { NationalIndicatorResponse } from "~/types/api";

describe("fetchNationalIndicatorForYear", () => {
    let apiResponse: NationalIndicatorResponse;
    const granularity: GranularityType = "month";
    const year = 2025;

    beforeAll(async () => {
        apiResponse = await fetchNationalIndicatorForYear(year, granularity);
    });

    it("should return correct schema", () => {
        expect(apiResponse).toHaveProperty("metadata");
        expect(apiResponse).toHaveProperty("time_series");
    });

    it("should return correct time_series for specific year", () => {
        const result = {
            date_start: `${year}-01-01`,
            date_end: `${year}-12-31`,
            baseline: "1991-2020",
            granularity: granularity,
            slice_type: "full",
        };

        expect(apiResponse.metadata).toStrictEqual(result);
    });

    it("should return correct time_series for specific year", () => {
        const timeSeries = apiResponse.time_series;

        expect(timeSeries).toHaveLength(12);
        expect(timeSeries[0]).toMatchObject({
            date: expect.any(String),
            temperature: expect.any(Number),
            baseline_mean: expect.any(Number),
            baseline_std_dev_upper: expect.any(Number),
            baseline_std_dev_lower: expect.any(Number),
            baseline_max: expect.any(Number),
            baseline_min: expect.any(Number),
        });
    });
});
