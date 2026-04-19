import type { NationalIndicatorResponse } from "~/types/api";
import type { GranularityType } from "~/components/ui/commons/selectBar/types";

export type ApiFetchFn = <T>(endpoint: string, opts?: object) => Promise<T>;

export async function fetchNationalIndicatorForYear(
    apiFetch: ApiFetchFn,
    year: number,
    granularity: GranularityType,
): Promise<NationalIndicatorResponse> {
    return apiFetch<NationalIndicatorResponse>(
        "/temperature/national-indicator",
        {
            query: {
                date_start: `${year}-01-01`,
                date_end: `${year}-12-31`,
                granularity,
                slice_type: "full",
            },
        },
    );
}

export async function fetchStackedData(
    years: number[],
    cache: Map<number, NationalIndicatorResponse>,
    fetchFn: (year: number) => Promise<NationalIndicatorResponse>,
): Promise<NationalIndicatorResponse | null> {
    if (years.length === 0) {
        return null;
    }

    const uniqueYears = [...new Set(years)];

    try {
        const responses = await Promise.all(
            uniqueYears.map(async (year) => {
                const cached = cache.get(year);

                if (cached) {
                    return cached;
                }

                const result = await fetchFn(year);
                cache.set(year, result);

                return result;
            }),
        );

        return {
            metadata: responses[0]!.metadata,
            time_series: responses.flatMap((r) => r.time_series),
        };
    } catch {
        return null;
    }
}
