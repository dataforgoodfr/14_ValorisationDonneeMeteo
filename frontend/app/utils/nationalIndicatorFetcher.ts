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
