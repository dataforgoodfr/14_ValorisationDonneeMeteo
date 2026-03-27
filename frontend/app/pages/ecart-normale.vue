<script setup lang="ts">
import PagesHero from "~/components/layout/PagesHero.vue";
import ChartLayout from "~/components/layout/ChartLayout.vue";
import SearchStation from "~/components/ecartNormale/searchStation.vue";
import { useDeviationSelectBarAdapter } from "~/adapters/deviationSelectBarAdapter";
import SelectBar from "~/components/ui/commons/selectBar/selectBar.vue";
import DeviationChart from "~/components/charts/DeviationChart.vue";
import DeviationTable from "~/components/table/deviation/DeviationTable.vue";
import type { ChartType } from "~/components/ui/commons/selectBar/types";
import MapD3 from "~/components/charts/MapD3.vue";

const selectBarAdapter = useDeviationSelectBarAdapter();
const chartType = computed<ChartType>(
    () => selectBarAdapter.chartType?.value ?? "bar",
);

const heroData = {
    title: "Ecart à la normale",
    description:
        'L\'écart à la normale est la différence entre la moyenne des températures sur une période, et les températures normales. Les " normales " sont calculées sur 30 ans et mises à jour toutes les décennies.',
};
</script>

<template>
    <UContainer class="flex flex-col gap-y-16">
        <PagesHero
            :title="heroData.title"
            :description="heroData.description"
        />
        <DeviationTable />
        <ChartLayout :has-sidebar="true">
            <template #select-bar>
                <SelectBar :adapter="selectBarAdapter" />
            </template>
            <template #sidebar>
                <SearchStation />
            </template>
            <template #chart>
                <ClientOnly>
                    <DeviationChart
                        :adapter="selectBarAdapter"
                        :chart-type="chartType"
                        class="px-3 py-2"
                    />
                </ClientOnly>
            </template>
        </ChartLayout>
        <div class="flex justify-center gap-8">
            <MapD3 mode="points" />
            <MapD3 mode="heatmap" />
        </div>
        <div class="flex justify-center gap-8">
            <!-- <MapD3 mode="stationsPoints" date="2025-01-01" />
            <MapD3 mode="stationsPoints" date="2025-04-01" />
            <MapD3 mode="stationsPoints" date="2025-07-01" /> -->
            <MapD3 mode="stationsPoints" date="2025-10-01" />
        </div>
        <div class="flex justify-center gap-8">
            <!-- <MapD3 mode="heatmapStationsTemp" date="2025-01-01" />
            <MapD3 mode="heatmapStationsTemp" date="2025-04-01" />
            <MapD3 mode="heatmapStationsTemp" date="2025-07-01" /> -->
            <MapD3 mode="heatmapStationsTemp" date="2025-10-01" />
        </div>
        <!-- <div class="flex justify-center gap-8">
            <MapD3 mode="stationsPoints" date="2025-07-01" />
            <MapD3 mode="stationsPoints" date="2025-10-01" />
            <MapD3 mode="stationsPoints" date="2025-12-01" />
        </div>
        <div class="flex justify-center gap-8">
            <MapD3 mode="stations" :stationType="0" />
            <MapD3 mode="stations" :stationType="2" />
        </div> -->
    </UContainer>
</template>
