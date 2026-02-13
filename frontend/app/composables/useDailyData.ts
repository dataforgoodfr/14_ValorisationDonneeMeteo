import type {
    DailyDataFilters,
    DailyMeasurement,
    PaginatedResponse,
} from "~/types/api";

export function useDailyData(filters?: MaybeRef<DailyDataFilters>) {
    const { useApiFetch } = useApiClient();

    return useApiFetch<PaginatedResponse<DailyMeasurement>>("/quotidien/", {
        query: filters,
    });
}
