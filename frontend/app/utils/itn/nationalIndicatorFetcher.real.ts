import type { NationalIndicatorResponse } from "~/types/api";
import type { GranularityType } from "~/components/ui/commons/selectBar/types";
import { useApiClient } from "~/composables/useApiClient";
import type { NationalIndicatorForYearFetcher } from "./nationalIndicatorFetcher";

const { apiFetch } = useApiClient();

export const fetchNationalIndicatorForYear: NationalIndicatorForYearFetcher =
    function (
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
    };
