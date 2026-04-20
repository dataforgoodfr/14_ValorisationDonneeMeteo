import type { NationalIndicatorResponse } from "~/types/api";
import type { GranularityType } from "~/components/ui/commons/selectBar/types";

export type NationalIndicatorForYearFetcher = (
    year: number,
    granularity: GranularityType,
) => Promise<NationalIndicatorResponse>;

export async function fetchStackedData(
    years: number[],
    granularity: GranularityType,
    cache: Map<number, NationalIndicatorResponse>,
    nationalIndicatorForYearFetcher: NationalIndicatorForYearFetcher,
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

                const result = await nationalIndicatorForYearFetcher(
                    year,
                    granularity,
                );
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
