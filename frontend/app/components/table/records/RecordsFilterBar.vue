<script setup lang="ts">
import { refDebounced } from "@vueuse/core";
import { storeToRefs } from "pinia";
import { useRecordsTableStore } from "~/stores/recordsTableStore";
import FilterBar from "~/components/ui/commons/FilterBar.vue";
import type {
    FilterField,
    FilterOption,
    FilterValue,
} from "~/components/ui/commons/FilterBar.vue";
import type { StationFilters } from "~/types/api";
import { useStations } from "~/composables/useStations";

const filterFields: FilterField[] = [
    { id: "name", label: "Station", type: "string-async" },
    { id: "departement", label: "Département", type: "string" },
    { id: "record", label: "Température record", type: "number-range" },
    { id: "record_date", label: "Date du record", type: "date-range" },
];

const store = useRecordsTableStore();
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

const {
    data: stationsData,
    pending: stationPending,
    execute: fetchStations,
} = useStations(stationFilter, { immediate: false, watch: false });

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
    stationsData.value = undefined;
    stationHasMore.value = false;
    fetchStations();
});

// Preserve code→name for selected stations so chips resolve labels after
// search results are cleared. Updated at selection time when labels are available.
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
    if (id === "name" && value.type === "string") {
        updateSelectedStationOptions(value.values);
    }
    setFilter(id, value);
}

function onSearch(id: string, query: string) {
    if (id !== "name") {
        return;
    }

    searchQuery.value = query;

    // When the dropdown opens with an empty query, debouncedQuery won't
    // change (it's already ""), so the watcher won't fire — fetch directly.
    if (!query) {
        stationPage.value = 0;
        allStationOptions.value = [];
        stationsData.value = undefined;
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

// Merge live search results with selected-station options (deduped).
// Selected options are appended only when not already present in search results,
// so chips can always resolve code→name even when search results are cleared.
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
