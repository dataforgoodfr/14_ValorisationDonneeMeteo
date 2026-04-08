<script setup lang="ts">
import PagesHero from "~/components/layout/PagesHero.vue";
import RecordsTable from "~/components/table/records/recordsTable.vue";
import ChartLayout from "~/components/layout/ChartLayout.vue";
import SearchByTerritoryType from "~/components/records/SearchByTerritoryType.vue";
import SearchStation from "~/components/ecartNormale/searchStation.vue";
import { useRecordsSelectBarAdapter } from "~/adapters/recordsSelectBarAdapter";
import SelectBar from "~/components/ui/commons/selectBar/selectBar.vue";
import RecordsChart from "~/components/charts/recordsChart.vue";
import type { RecordsChartType } from "~/types/echarts.d";

const selectBarAdapter = useRecordsSelectBarAdapter();
const chartType = ref<RecordsChartType>("scatter");

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
                <div
                    class="flex rounded-md overflow-hidden border border-gray-600"
                >
                    <button
                        class="px-3 py-1 text-sm transition-colors"
                        :class="
                            chartType === 'scatter'
                                ? 'bg-blue-600 text-white'
                                : 'bg-transparent text-gray-400 hover:text-white'
                        "
                        @click="chartType = 'scatter'"
                    >
                        Nuage de points
                    </button>
                    <button
                        class="px-3 py-1 text-sm transition-colors"
                        :class="
                            chartType === 'pyramid'
                                ? 'bg-blue-600 text-white'
                                : 'bg-transparent text-gray-400 hover:text-white'
                        "
                        @click="chartType = 'pyramid'"
                    >
                        Pyramide
                    </button>
                </div>
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
