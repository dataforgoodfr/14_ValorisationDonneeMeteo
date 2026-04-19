import { describe, it, expect, vi } from "vitest";
import { fetchStackedData } from "~/utils/nationalIndicatorFetcher";
import type { NationalIndicatorResponse } from "~/types/api";

describe("fetchStackedData", () => {
    it("should not fetch already cached years", async () => {
        const cacheTest = new Map<number, NationalIndicatorResponse>();
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

        const mockFetch = vi.fn().mockResolvedValue(result);

        await fetchStackedData([2025, 2026, 2025], cacheTest, mockFetch);

        expect(mockFetch).toHaveBeenCalledTimes(2);

        expect(cacheTest.keys()).toContain(2025);
        expect(cacheTest.keys()).toContain(2026);
    });

    it("should return null if no year is selected", async () => {
        const fetchFunction = vi.fn();
        const response = await fetchStackedData([], new Map(), fetchFunction);

        expect(response).toBeNull();
    });
});
