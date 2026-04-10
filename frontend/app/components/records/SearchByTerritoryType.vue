<script setup lang="ts">
import type { SelectItem } from "@nuxt/ui";

import SearchByDepartment from "./SearchByDepartment.vue";
import SearchByRegion from "./SearchByRegion.vue";
import SearchByTerritory from "./SearchByTerritory.vue";
import SearchByStation from "./SearchByStation.vue";
import { useRecordsChartStore } from "#imports";

const store = useRecordsChartStore();
const { selectedElements } = storeToRefs(store);
const { removeItemFromFilter } = store;

const searchQuery = ref<undefined | string>("");

const selectedTerritoryType = ref<TerritoryFilterType>(
    TerritoryFilterType.STATION,
);
const TERRITORY_OPTIONS = ref<SelectItem[]>([
    { label: "Par station", value: TerritoryFilterType.STATION },
    { label: "Par département", value: TerritoryFilterType.DEPARTMENT },
    { label: "Par région", value: TerritoryFilterType.REGION },
    { label: "Par territoire", value: TerritoryFilterType.TERRITORY },
]);

function onUnselectElement(
    _event: PointerEvent,
    element: {
        value: string;
        id: string;
        type: TerritoryFilterType;
    },
) {
    removeItemFromFilter(element.type, element.id);
}
</script>
<template>
    <div class="flex flex-col gap-2 w-64 p-4 h-full max-h-158">
        <USelect
            v-model="selectedTerritoryType"
            :items="TERRITORY_OPTIONS"
            option-label="label"
            placeholder="Type de filtre"
            class="w-full"
            show-clear
        />
        <UInput
            v-model="searchQuery"
            trailing-icon="i-lucide-search"
            size="md"
            variant="outline"
            placeholder="Rechercher"
        />

        <div
            v-if="selectedElements.length > 0"
            class="max-h-44 overflow-y-auto shrink-0"
        >
            <ul>
                <li
                    v-for="selectedElement in selectedElements"
                    :key="`selected-${selectedElement.value}`"
                    :title="selectedElement.value"
                    class="cursor-pointer pr-2 font-bold py-1 text-sm flex items-center justify-between"
                    @click="onUnselectElement($event, selectedElement)"
                >
                    <span class="truncate">{{ selectedElement.value }}</span>
                    <UIcon name="i-lucide-x" class="shrink-0" />
                </li>
            </ul>
        </div>

        <USeparator v-if="selectedElements.length > 0" />

        <SearchByStation
            v-if="selectedTerritoryType === TerritoryFilterType.STATION"
            :search-query="searchQuery"
        />

        <SearchByDepartment
            v-if="selectedTerritoryType === TerritoryFilterType.DEPARTMENT"
            :search-query="searchQuery"
        />
        <SearchByRegion
            v-if="selectedTerritoryType === TerritoryFilterType.REGION"
            :search-query="searchQuery"
        />
        <SearchByTerritory
            v-if="selectedTerritoryType === TerritoryFilterType.TERRITORY"
            :search-query="searchQuery"
        />
    </div>
</template>
