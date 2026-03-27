<script setup lang="ts">
import PagesHero from "~/components/layout/PagesHero.vue";
import Barchart from "~/components/charts/Barchart.vue";
import LineChart from "~/components/charts/LineChart.vue";
import ChartLayout from "~/components/layout/ChartLayout.vue";
import ChartSidebar from "~/components/ui/commons/ChartSidebar.vue";
import { useDeviationSelectBarAdapter } from "~/adapters/deviationSelectBarAdapter";
import SelectBar from "~/components/ui/commons/selectBar/selectBar.vue";
import MapD3 from "~/components/charts/MapD3.vue";

const selectBarAdapter = useDeviationSelectBarAdapter();

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
        <ChartLayout :has-sidebar="true">
            <template #select-bar>
                <SelectBar :adapter="selectBarAdapter" />
            </template>
            <template #sidebar>
                <ChartSidebar />
            </template>
            <template #chart>
                <Barchart v-if="selectBarAdapter.chartType?.value === `bar`" />
                <LineChart
                    v-if="selectBarAdapter.chartType?.value === `line`"
                />
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
