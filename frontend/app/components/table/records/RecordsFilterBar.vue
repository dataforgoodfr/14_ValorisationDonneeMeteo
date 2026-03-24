<script setup lang="ts">
import { storeToRefs } from "pinia";
import { useRecordsStore } from "~/stores/recordsStore";
import FilterBar from "~/components/ui/commons/FilterBar.vue";
import type { FilterField } from "~/components/ui/commons/FilterBar.vue";

const filterFields: FilterField[] = [
    { id: "name", label: "Station", type: "string" },
    { id: "ville", label: "Ville", type: "string" },
    { id: "departement", label: "Département", type: "string" },
    { id: "date_creation", label: "Date création station", type: "date-range" },
    { id: "record", label: "Température record", type: "number-range" },
    { id: "record_date", label: "Date du record", type: "date-range" },
];

const store = useRecordsStore();
const { stringFilters, rangeFilters, recordType } = storeToRefs(store);
const { setStringFilter, setRangeFilter, clearFilter } = store;
</script>

<template>
    <FilterBar
        :fields="filterFields"
        :unique-values="store.uniqueValues"
        :string-filters="stringFilters"
        :range-filters="rangeFilters"
        @update:string-filter="setStringFilter"
        @update:range-filter="setRangeFilter"
        @clear="clearFilter"
    >
        <template #actions>
            <UFieldGroup class="ml-auto">
                <UButton
                    class="cursor-pointer"
                    color="neutral"
                    :variant="recordType === 'Chaud' ? 'subtle' : 'outline'"
                    label="Chaud"
                    @click="recordType = 'Chaud'"
                />
                <UButton
                    class="cursor-pointer"
                    color="neutral"
                    :variant="recordType === 'Froid' ? 'subtle' : 'outline'"
                    label="Froid"
                    @click="recordType = 'Froid'"
                />
            </UFieldGroup>
        </template>
    </FilterBar>
</template>
