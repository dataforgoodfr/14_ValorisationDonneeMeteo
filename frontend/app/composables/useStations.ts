import type {
    PaginatedResponse,
    Station,
    StationDetail,
    StationFilters,
} from "~/types/api";

const DEFAULT_STATIONS_ENDPOINT = "/stations/";

export function useStations(
    filters: MaybeRef<StationFilters>,
    options?: Record<string, unknown>,
    endpoint: string = DEFAULT_STATIONS_ENDPOINT,
) {
    const { useApiFetch } = useApiClient();

    return useApiFetch<PaginatedResponse<Station>>(endpoint, {
        query: filters,
        watch: [filters],
        immediate: true,
        ...options,
    });
}

export function useStationsWithInfiniteScroll(
    filters: MaybeRef<StationFilters>,
    endpoint: string = DEFAULT_STATIONS_ENDPOINT,
) {
    const allStations = ref<Station[]>([]);
    const hasMore = ref<boolean>(false);
    const page = ref<number>(0);

    const params = computed(() => ({
        ...toValue(filters),
        offset: page.value * 100,
    }));

    const { data: stationsData } = useStations(
        params,
        {
            watch: [params],
            immediate: true,
            server: false,
        },
        endpoint,
    );

    function processStations(newData: PaginatedResponse<Station> | undefined) {
        if (!newData) return;
        if (toValue(page) === 0) {
            allStations.value = newData.results;
        } else {
            allStations.value = [...allStations.value, ...newData.results];
        }
        hasMore.value = !!newData.next;
    }

    function onLoadMore() {
        page.value = page.value + 1;
    }

    watch([filters], () => {
        page.value = 0;
    });

    watch(
        stationsData,
        (newData) => {
            processStations(newData);
        },
        { immediate: true },
    );

    return {
        allStations,
        onLoadMore,
        hasMore,
    };
}

export function useStation(
    id: MaybeRef<number | string>,
    endpoint: string = DEFAULT_STATIONS_ENDPOINT,
) {
    const { useApiFetch } = useApiClient();

    return useApiFetch<StationDetail>(() => `${endpoint}${toValue(id)}/`);
}
