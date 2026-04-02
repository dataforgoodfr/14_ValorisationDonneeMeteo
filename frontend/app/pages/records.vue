<script setup lang="ts">
import PagesHero from "~/components/layout/PagesHero.vue";
import RecordsTable from "~/components/table/records/recordsTable.vue";
import ChartLayout from "~/components/layout/ChartLayout.vue";
import SearchByTerritoryType from "~/components/records/SearchByTerritoryType.vue";
import SearchStation from "~/components/ecartNormale/searchStation.vue";
import { useRecordsSelectBarAdapter } from "~/adapters/recordsSelectBarAdapter";
import SelectBar from "~/components/ui/commons/selectBar/selectBar.vue";
import RecordsChart from "~/components/charts/recordsChart.vue";

const selectBarAdapter = useRecordsSelectBarAdapter();

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
        <div class="flex gap-24 flex-col">
            <RecordsTable />
            <ChartLayout :has-sidebar="true">
                <template #select-bar> </template>
                <template #sidebar>
                    <SearchByTerritoryType />
                </template>
                <template #chart> </template>
            </ChartLayout>
        </div>
    </UContainer>
</template>
