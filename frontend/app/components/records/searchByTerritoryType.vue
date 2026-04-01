<script setup lang="ts">
import type { SelectItem } from "@nuxt/ui";

import SearchByDepartment from "./searchByDepartment.vue";
import SearchByStation from "./searchByStation.vue";
import type { Station } from "~/types/api";

const store = useRecordsGraphStore();
const { selectedElements } = storeToRefs(store);
const { removeDepartmentFilter, removeStationFilter } = store;

const searchQuery = ref<undefined | string>("");

const selectedTerritoryType = ref<string>("STATION");
const TERRITORY_OPTIONS = ref<SelectItem[]>([
    { label: "Par station", value: "STATION" },
    { label: "Par département", value: "DEPARTEMENT" },
    { label: "Par territoire", value: "TERRITORY" },
]);

function onUnselectElement(
    _event: PointerEvent,
    element: {
        value: string;
        item: Station | { code: string; name: string };
        type: string;
    },
) {
    console.log("unselect", element);
    if (element.type === "STATION") {
        removeStationFilter(element.item as Station);
    } else if (element.type === "DEPARTMENT") {
        removeDepartmentFilter(element.item as { code: string; name: string });
    }
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
        <SearchByDepartment v-if="selectedTerritoryType === 'DEPARTEMENT'" />
        <SearchByStation
            v-else-if="selectedTerritoryType === 'STATION'"
            :search-query="searchQuery"
        />
    </div>
</template>
