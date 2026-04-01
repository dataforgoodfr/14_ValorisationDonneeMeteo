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
        watch: [filters],
        immediate: true,
        ...options,
    });
}

export function useStationsWithInfiniteScroll(
    filters?: MaybeRef<StationFilters>,
) {
    console.log("Stations infinite scroll", { filters });
    const allStations = ref<Station[]>([]);
    const hasMore = ref<boolean>(false);
    const page = ref<number>(0);

    const params = computed(() => {
        const val = {
            ...toValue(filters),
            offset: page.value * 100,
        };
        console.log("params recomputed:", val); // ← est-ce que search apparaît ?
        return val;
    });

    const { data: stationsData, refresh } = useStations(params);

    function processStations(newData: PaginatedResponse<Station> | undefined) {
        if (!newData) return;
        if (toValue(page) === 0) {
            allStations.value = newData.results;
        } else {
            allStations.value = [...allStations.value, ...newData.results];
        }
        hasMore.value = !!newData.next;
    }

    async function onRefresh() {
        page.value = page.value + 1;
        await refresh();
        processStations(stationsData.value);
    }

    watch(
        () => toValue(filters),
        async () => {
            page.value = 0;
            await refresh();
            processStations(stationsData.value);
        },
    );

    return {
        allStations,
        onRefresh,
        hasMore,
    };
}

export function useStation(id: MaybeRef<number | string>) {
    const { useApiFetch } = useApiClient();

    return useApiFetch<StationDetail>(() => `/stations/${toValue(id)}/`);
}
