import { describe, expect, it } from "vitest";
import type { NationalIndicatorResponse } from "~/types/api";
import {
    fetchStackedData,
    type NationalIndicatorForYearFetcher,
} from "./nationalIndicatorFetcher";

describe("fetchStackedData", () => {
    const calledYears: Map<number, number> = new Map();

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

    const fakeFetchFn: NationalIndicatorForYearFetcher = async function (
        year: number,
    ): Promise<NationalIndicatorResponse> {
        calledYears.set(year, (calledYears.get(year) ?? 0) + 1);
        return result;
    };

    it("should not fetch already cached years", async () => {
        const cache = new Map<number, NationalIndicatorResponse>();

        await fetchStackedData([2025, 2026], "month", cache, fakeFetchFn);
        await fetchStackedData([2025, 2026, 2027], "month", cache, fakeFetchFn);

        expect(calledYears.get(2025)).toEqual(1);
        expect(calledYears.get(2026)).toEqual(1);
        expect(calledYears.get(2027)).toEqual(1);
    });

    it("should return null if no year is selected", async () => {
        const response = await fetchStackedData(
            [],
            "month",
            new Map(),
            fakeFetchFn,
        );

        expect(response).toBeNull();
    });
});
