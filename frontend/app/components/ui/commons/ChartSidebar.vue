<script setup lang="ts">
import type { Station } from "~/types/api";
import SearchStation from "./searchStation.vue";

const deviationStore = useDeviationStore();
const { stationIds, selectedStations } = storeToRefs(deviationStore);

function onSelect(station: Station) {
    if (stationIds.value && stationIds.value.length > 0) {
        deviationStore.setStations([
            ...deviationStore.selectedStations,
            station,
        ]);
    } else {
        deviationStore.setStations([station]);
    }
}

function onUnselect(station: Station) {
    if (!deviationStore.setStations) return;
    deviationStore.setStations(
        deviationStore.selectedStations.filter((s) => s.code !== station.code),
    );
}
</script>

<template>
    <div class="w-64 p-4 flex flex-col gap-4">
        <div class="flex flex-col gap-2">
            <SearchStation
                :selected-stations="selectedStations"
                :on-select="onSelect"
                :on-unselect="onUnselect"
            />
        </div>
    </div>
</template>
