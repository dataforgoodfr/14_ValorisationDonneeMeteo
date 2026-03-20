<script setup lang="ts">
import PagesHero from "~/components/layout/PagesHero.vue";
import ChartLayout from "~/components/layout/ChartLayout.vue";
import ChartSidebar from "~/components/ui/commons/ChartSidebar.vue";
import { useDeviationSelectBarAdapter } from "~/adapters/deviationSelectBarAdapter";
import SelectBar from "~/components/ui/commons/selectBar/selectBar.vue";
<<<<<<< HEAD
import DeviationChart from "~/components/charts/DeviationChart.vue";
=======
import SearchStation from "~/components/ui/commons/searchStation.vue";
import type { Station } from "~/types/api";
>>>>>>> 476b759 (fix: ecart-normale: fix SearchStation to be generic)

const selectBarAdapter = useDeviationSelectBarAdapter();

const heroData = {
    title: "Ecart à la normale",
    description:
        'L\'écart à la normale est la différence entre la moyenne des températures sur une période, et les températures normales. Les " normales " sont calculées sur 30 ans et mises à jour toutes les décennies.',
};

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
    <UContainer class="flex flex-col gap-y-16">
        <PagesHero
            :title="heroData.title"
            :description="heroData.description"
        />
        <ChartLayout :has-sidebar="true">
            <template #select-bar>
                <SelectBar :adapter="selectBarAdapter" />
            </template>
            <template #sidebar>
                <ChartSidebar />
                <SearchStation
                    :selected-stations="selected_stations"
                    :on-select="onSelect"
                    :on-unselect="onUnselect"
                />
            </template>
            <template #chart>
                <DeviationChart :adapter="selectBarAdapter" class="px-3 py-2" />
            </template>
        </ChartLayout>
    </UContainer>
</template>
