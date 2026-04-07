import type {
    PaginatedResponse,
    Station,
    StationDetail,
    StationFilters,
} from "~/types/api";

export function useStations(
    filters?: MaybeRef<StationFilters>,
    options?: Record<string, unknown>,
) {
    const { useApiFetch } = useApiClient();

    return useApiFetch<PaginatedResponse<Station>>("/stations/", {
        query: filters,
        ...options,
    });
}

export function useStation(id: MaybeRef<number | string>) {
    const { useApiFetch } = useApiClient();

    return useApiFetch<StationDetail>(() => `/stations/${toValue(id)}/`);
}
