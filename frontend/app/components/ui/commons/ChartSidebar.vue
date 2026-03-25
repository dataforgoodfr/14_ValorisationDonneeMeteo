<script setup lang="ts">
import type { Station } from "~/types/api";
import SearchStation from "./searchStation.vue";

const deviationStore = useDeviationStore();
const { station_ids, selected_stations } = storeToRefs(deviationStore);

function onSelect(station: Station) {
    if (station_ids.value && station_ids.value.length > 0) {
        deviationStore.setStations([
            ...deviationStore.selected_stations,
            station,
        ]);
    } else {
        deviationStore.setStations([station]);
    }
}

function onUnselect(station: Station) {
    if (!deviationStore.setStations) return;
    deviationStore.setStations(
        deviationStore.selected_stations.filter((s) => s.code !== station.code),
    );
}
</script>

<template>
    <div class="w-64 p-4 flex flex-col gap-4">
        <div class="flex flex-col gap-2">
            <SearchStation
                :selected-stations="selected_stations"
                :on-select="onSelect"
                :on-unselect="onUnselect"
            />
        </div>
    </div>
</template>
