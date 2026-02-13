import type {
    PaginatedResponse,
    Station,
    StationDetail,
    StationFilters,
} from "~/types/api";

export function useStations(filters?: MaybeRef<StationFilters>) {
    const { useApiFetch } = useApiClient();

    return useApiFetch<PaginatedResponse<Station>>("/stations/", {
        query: filters,
    });
}

export function useStation(id: MaybeRef<number | string>) {
    const { useApiFetch } = useApiClient();

    return useApiFetch<StationDetail>(() => `/stations/${toValue(id)}/`);
}
