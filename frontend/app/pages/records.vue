<script setup lang="ts">
import PagesHero from "~/components/layout/PagesHero.vue";
import RecordsTable from "~/components/table/records/recordsTable.vue";
import ChartLayout from "~/components/layout/ChartLayout.vue";
import SearchStation from "~/components/ecartNormale/searchStation.vue";
import { useRecordsSelectBarAdapter } from "~/adapters/recordsSelectBarAdapter";
import SelectBar from "~/components/ui/commons/selectBar/selectBar.vue";
import RecordsChart from "~/components/charts/recordsChart.vue";
import type { ChartType } from "~/components/ui/commons/selectBar/types";

const selectBarAdapter = useRecordsSelectBarAdapter();
const chartType = computed<ChartType>(
    () => selectBarAdapter.chartType?.value ?? "scatter",
);

const heroData = {
    title: "Records",
    description:
        "Tableau des stations météo ayant enregistrées un record de température sur une période donnée.",
};
</script>

<template>
    <UContainer class="flex flex-col gap-y-16">
        <PagesHero
            :title="heroData.title"
            :description="heroData.description"
        />
        <RecordsTable />
        <ChartLayout :has-sidebar="true">
            <template #select-bar>
                <SelectBar :adapter="selectBarAdapter" />
            </template>
            <template #sidebar>
                <SearchStation />
            </template>
            <template #chart>
                <RecordsChart
                    :adapter="selectBarAdapter"
                    :chart-type="chartType"
                    class="px-3 py-2"
                />
            </template>
        </ChartLayout>
    </UContainer>
</template>
