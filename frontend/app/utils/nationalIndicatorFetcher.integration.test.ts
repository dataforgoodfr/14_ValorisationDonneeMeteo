import { $fetch } from "ofetch";
import { describe, it, expect, beforeAll } from "vitest";
import { fetchNationalIndicatorForYear } from "~/utils/nationalIndicatorFetcher";

import type { GranularityType } from "~/components/ui/commons/selectBar/types";
import type { NationalIndicatorResponse } from "~/types/api";

const testApiFetch = <T>(
    endpoint: string,
    options?: Parameters<typeof $fetch<T>>[1],
): Promise<T> =>
    $fetch<T>(endpoint, {
        baseURL: import.meta.env.NUXT_PUBLIC_API_BASE,
        ...options,
    });

describe("fetchNationalIndicatorForYear", () => {
    let apiResponse: NationalIndicatorResponse;
    const granularity: GranularityType = "month";
    const year = 2025;

    beforeAll(async () => {
        apiResponse = await fetchNationalIndicatorForYear(
            testApiFetch,
            2025,
            granularity,
        );
    });

    it("should return correct schema", async () => {
        expect(apiResponse).toHaveProperty("metadata");
        expect(apiResponse).toHaveProperty("time_series");
    });

    it("should return correct time_series for specific year", async () => {
        const result = {
            date_start: `${year}-01-01`,
            date_end: `${year}-12-31`,
            baseline: "1991-2020",
            granularity: granularity,
            slice_type: "full",
        };

        expect(apiResponse.metadata).toStrictEqual(result);
    });

    it("should return correct time_series for specific year", async () => {
        const timeSeries = apiResponse.time_series;

        expect(timeSeries.length).toBe(12);
        expect(timeSeries[0]).toHaveProperty("date");
        expect(timeSeries[0]).toHaveProperty("temperature");
        expect(timeSeries[0]).toHaveProperty("baseline_mean");
        expect(timeSeries[0]).toHaveProperty("baseline_std_dev_upper");
        expect(timeSeries[0]).toHaveProperty("baseline_std_dev_lower");
        expect(timeSeries[0]).toHaveProperty("baseline_max");
        expect(timeSeries[0]).toHaveProperty("baseline_min");
    });
});
