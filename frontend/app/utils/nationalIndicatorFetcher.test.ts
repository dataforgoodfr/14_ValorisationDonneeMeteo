import { describe, it, expect } from "vitest";
import {
    fetchNationalIndicatorForYear,
    fetchStackedData,
} from "~/utils/nationalIndicatorFetcher";
import type { GranularityType } from "~/components/ui/commons/selectBar/types";
import type { NationalIndicatorResponse } from "~/types/api";

describe("fetchNationalIndicatorForYear", () => {
    let capturedEndpoint: string = "";
    let capturedOpts: unknown;
    const fakeApiFetch = async <NationalIndicatorResponse>(
        endpoint: string,
        options?: Parameters<typeof $fetch<NationalIndicatorResponse>>[1],
    ): Promise<NationalIndicatorResponse> => {
        capturedEndpoint = endpoint;
        capturedOpts = options;

        return {} as NationalIndicatorResponse;
    };

    it("should call the correct endpoint", async () => {
        await fetchNationalIndicatorForYear(fakeApiFetch, 2023, "month");

        expect(capturedEndpoint).toBe("/temperature/national-indicator");
    });

    it.each([
        { year: 2024, granularity: "month" },
        { year: 2020, granularity: "year" },
        { year: 2016, granularity: "day" },
    ])(
        "should build query params for year $year and granularity $granularity",
        async ({ year, granularity }) => {
            await fetchNationalIndicatorForYear(
                fakeApiFetch,
                year,
                granularity as GranularityType,
            );

            expect(capturedOpts).toEqual({
                query: {
                    granularity,
                    date_start: `${year}-01-01`,
                    date_end: `${year}-12-31`,
                    slice_type: "full",
                },
            });
        },
    );
});

describe("fetchStackedData", () => {
    let fetchCallCount: number = 0;
    const result: NationalIndicatorResponse = {
        metadata: {
            date_start: "2025-01-01",
            date_end: "2025-12-31",
            baseline: "1991-2020",
            granularity: "month",
            slice_type: "full",
        },
        time_series: [],
    };

    async function fakeFetchFn(): Promise<NationalIndicatorResponse> {
        fetchCallCount++;

        return result;
    }

    it("should not fetch already cached years", async () => {
        const cacheTest = new Map<number, NationalIndicatorResponse>();

        await fetchStackedData([2025, 2026, 2025], cacheTest, fakeFetchFn);

        expect(fetchCallCount).toBe(2);

        expect(cacheTest.keys()).toContain(2025);
        expect(cacheTest.keys()).toContain(2026);
    });

    it("should return null if no year is selected", async () => {
        const response = await fetchStackedData([], new Map(), fakeFetchFn);

        expect(response).toBeNull();
    });
});
