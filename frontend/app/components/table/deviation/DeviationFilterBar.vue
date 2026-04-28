<script setup lang="ts">
import { refDebounced } from "@vueuse/core";
import { storeToRefs } from "pinia";
import { useDeviationTableStore } from "~/stores/deviationTableStore";
import FilterBar from "~/components/ui/commons/FilterBar.vue";
import type {
    FilterField,
    FilterOption,
    FilterValue,
} from "~/components/ui/commons/FilterBar.vue";
import type { PaginatedResponse, Station, StationFilters } from "~/types/api";

const filterFields: FilterField[] = [
    { id: "name", label: "Station", type: "string-async" },
    { id: "departement", label: "Département", type: "string" },
    { id: "region", label: "Région", type: "string" },
    // { id: "altitude", label: "Altitude", type: "number-range", unit: "m" },
    {
        id: "deviation",
        label: "Écart à la normale",
        type: "number-range",
        unit: "°C",
    },
    {
        id: "temperatureMean",
        label: "Température moyenne",
        type: "number-range",
        unit: "°C",
    },
];

const store = useDeviationTableStore();
const { filters } = storeToRefs(store);
const { setFilter, clearFilter } = store;

const searchQuery = ref("");
const debouncedQuery = refDebounced(searchQuery, 300);
const stationPage = ref(0);
const allStationOptions = ref<FilterOption[]>([]);
const stationHasMore = ref(false);

const stationFilter = computed<StationFilters>(() => ({
    search: debouncedQuery.value,
    limit: 20,
    offset: stationPage.value * 20,
}));

const { apiFetch } = useApiClient();
const stationPending = ref(false);
const stationsData = ref<PaginatedResponse<Station> | null>(null);

async function fetchStations() {
    stationPending.value = true;
    try {
        stationsData.value = await apiFetch<PaginatedResponse<Station>>(
            "/stations/",
            { query: stationFilter.value },
        );
    } finally {
        stationPending.value = false;
    }
}

watch(stationsData, (newData) => {
    if (!newData) return;
    const newOptions = newData.results.map((s) => ({
        value: s.code,
        label: s.nom,
    }));
    if (stationPage.value === 0) {
        allStationOptions.value = newOptions;
    } else {
        allStationOptions.value = [...allStationOptions.value, ...newOptions];
    }
    stationHasMore.value = !!newData.next;
});

watch(debouncedQuery, () => {
    stationPage.value = 0;
    allStationOptions.value = [];
    stationsData.value = null;
    stationHasMore.value = false;
    fetchStations();
});

const selectedStationOptions = ref<FilterOption[]>([]);

function updateSelectedStationOptions(codes: string[]) {
    const knownLabels = new Map(
        [...selectedStationOptions.value, ...allStationOptions.value].map(
            (o) => [o.value, o.label],
        ),
    );
    selectedStationOptions.value = codes.map((code) => ({
        value: code,
        label: knownLabels.get(code) ?? code,
    }));
}

function onUpdateFilter(id: string, value: FilterValue) {
    if (id === "name" && value.type === "string")
        updateSelectedStationOptions(value.values);
    setFilter(id, value);
}

function onSearch(id: string, query: string) {
    if (id !== "name") return;
    searchQuery.value = query;
    if (!query) {
        stationPage.value = 0;
        allStationOptions.value = [];
        stationsData.value = null;
        stationHasMore.value = false;
        fetchStations();
    }
}

function onLoadMore(id: string) {
    if (id === "name" && stationHasMore.value) {
        stationPage.value++;
        fetchStations();
    }
}

const filterOptions = computed(() => {
    const searchResults = allStationOptions.value;
    const searchResultCodes = new Set(searchResults.map((o) => o.value));
    const extraSelected = selectedStationOptions.value.filter(
        (o) => !searchResultCodes.has(o.value),
    );
    return {
        ...store.staticOptions,
        name: [...searchResults, ...extraSelected],
    };
});
</script>

<template>
    <FilterBar
        :fields="filterFields"
        :filter-options="filterOptions"
        :filters="filters"
        :async-pending="{ name: stationPending }"
        :async-has-more="{ name: stationHasMore }"
        @update:filter="onUpdateFilter"
        @clear="clearFilter"
        @search="onSearch"
        @load-more="onLoadMore"
    />
</template>
