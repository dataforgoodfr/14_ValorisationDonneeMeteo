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
        stationsData.value = null;
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

function onSearch(id: string, query: string) {
    if (id === "name") searchQuery.value = query;
}

const uniqueValues = computed(() => ({
    ...store.uniqueValues,
    name: stationOptions.value,
}));
</script>

<template>
    <FilterBar
        :fields="filterFields"
        :unique-values="uniqueValues"
        :string-filters="stringFilters"
        :range-filters="rangeFilters"
        :async-pending="{ name: stationPending }"
        @update:string-filter="setStringFilter"
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
