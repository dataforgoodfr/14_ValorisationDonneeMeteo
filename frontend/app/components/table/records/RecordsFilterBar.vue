<script setup lang="ts">
import { refDebounced } from "@vueuse/core";
import { storeToRefs } from "pinia";
import { useRecordsStore } from "~/stores/recordsStore";
import FilterBar from "~/components/ui/commons/FilterBar.vue";
import type {
    FilterField,
    FilterOption,
} from "~/components/ui/commons/FilterBar.vue";
import type { StationFilters } from "~/types/api";
import { useStations } from "~/composables/useStations";

const filterFields: FilterField[] = [
    { id: "name", label: "Station", type: "string-async" },
    { id: "departement", label: "Département", type: "string" },
    { id: "record", label: "Température record", type: "number-range" },
    { id: "record_date", label: "Date du record", type: "date-range" },
];

const store = useRecordsStore();
const { stringFilters, rangeFilters, typeRecords } = storeToRefs(store);
const { setStringFilter, setRangeFilter, clearFilter } = store;

const searchQuery = ref("");
const debouncedQuery = refDebounced(searchQuery, 300);

const stationFilter = computed<StationFilters>(() => ({
    search: debouncedQuery.value,
    limit: 20,
}));

const {
    data: stationsData,
    pending: stationPending,
    execute: fetchStations,
} = useStations(stationFilter, { immediate: false, watch: false });

watch(debouncedQuery, (query) => {
    if (query) {
        stationsData.value = undefined;
        fetchStations();
    }
});

const stationOptions = computed<FilterOption[]>(() => {
    if (!debouncedQuery.value) return [];
    return (stationsData.value?.results ?? []).map((s) => ({
        value: s.code,
        label: s.nom,
    }));
});

// Preserve code→name for selected stations so chips resolve labels after
// search results are cleared. Updated at selection time when labels are available.
const selectedStationOptions = ref<FilterOption[]>([]);

function onUpdateStringFilter(id: string, values: string[]) {
    if (id === "name") {
        selectedStationOptions.value = values.map(
            (code) =>
                stationOptions.value.find((o) => o.value === code) ??
                selectedStationOptions.value.find((o) => o.value === code) ?? {
                    value: code,
                    label: code,
                },
        );
    }
    setStringFilter(id, values);
}

function onSearch(id: string, query: string) {
    if (id === "name") {
        searchQuery.value = query;
        if (!query) stationsData.value = undefined;
    }
}

// Merge live search results with selected-station options (deduped).
// Selected options are appended only when not already present in search results,
// so chips can always resolve code→name even when search results are cleared.
const filterOptions = computed(() => {
    const searchResults = stationOptions.value;
    const searchResultCodes = new Set(searchResults.map((o) => o.value));
    const extraSelected = selectedStationOptions.value.filter(
        (o) => !searchResultCodes.has(o.value),
    );
    return {
        ...store.uniqueValues,
        name: [...searchResults, ...extraSelected],
    };
});
</script>

<template>
    <FilterBar
        :fields="filterFields"
        :filter-options="filterOptions"
        :string-filters="stringFilters"
        :range-filters="rangeFilters"
        :async-pending="{ name: stationPending }"
        @update:string-filter="onUpdateStringFilter"
        @update:range-filter="setRangeFilter"
        @clear="clearFilter"
        @search="onSearch"
    >
        <template #actions>
            <UFieldGroup class="ml-auto">
                <UButton
                    class="cursor-pointer"
                    color="neutral"
                    :variant="typeRecords === 'hot' ? 'subtle' : 'outline'"
                    label="Chaud"
                    @click="typeRecords = 'hot'"
                />
                <UButton
                    class="cursor-pointer"
                    color="neutral"
                    :variant="typeRecords === 'cold' ? 'subtle' : 'outline'"
                    label="Froid"
                    @click="typeRecords = 'cold'"
                />
            </UFieldGroup>
        </template>
    </FilterBar>
</template>
