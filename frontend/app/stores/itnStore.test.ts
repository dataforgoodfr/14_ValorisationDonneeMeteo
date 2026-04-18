import { describe, it, expect } from "vitest";
import { fetchNationalIndicatorForYear } from "~/utils/nationalIndicatorFetcher";
import type { NationalIndicatorResponse } from "~/types/api";

const fakeResponse: NationalIndicatorResponse = {
    metadata: {
        date_start: "2023-01-01",
        date_end: "2023-12-31",
        baseline: "1991-2020",
        granularity: "month",
        slice_type: "full",
    },
    time_series: [],
};

describe("fetchNationalIndicatorForYear", () => {
    it("appelle /temperature/national-indicator", async () => {
        let capturedEndpoint = "";
        const fakeApiFetch = async <T>(endpoint: string): Promise<T> => {
            capturedEndpoint = endpoint;
            return fakeResponse as T;
        };

        await fetchNationalIndicatorForYear(fakeApiFetch, 2023, "month");

        expect(capturedEndpoint).toBe("/temperature/national-indicator");
    });

    it("construit les bonnes dates pour l'année donnée", async () => {
        let capturedOpts: unknown;
        const fakeApiFetch = async <T>(
            _: string,
            opts: unknown,
        ): Promise<T> => {
            capturedOpts = opts;
            return fakeResponse as T;
        };

        await fetchNationalIndicatorForYear(fakeApiFetch, 2023, "month");

        expect(capturedOpts).toEqual({
            query: {
                date_start: "2023-01-01",
                date_end: "2023-12-31",
                granularity: "month",
                slice_type: "full",
            },
        });
    });

    it("retourne la réponse du fetch", async () => {
        const fakeApiFetch = async <T>(): Promise<T> => fakeResponse as T;

        const result = await fetchNationalIndicatorForYear(
            fakeApiFetch,
            2023,
            "month",
        );

        expect(result).toBe(fakeResponse);
    });

    it("adapte les dates à l'année passée en paramètre", async () => {
        let capturedOpts: unknown;
        const fakeApiFetch = async <T>(
            _: string,
            opts: unknown,
        ): Promise<T> => {
            capturedOpts = opts;
            return fakeResponse as T;
        };

        await fetchNationalIndicatorForYear(fakeApiFetch, 1998, "day");

        expect(capturedOpts).toMatchObject({
            query: {
                date_start: "1998-01-01",
                date_end: "1998-12-31",
                granularity: "day",
            },
        });
    });
});
