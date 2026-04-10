<script setup lang="ts">
import PagesHero from "~/components/layout/PagesHero.vue";
import RecordsTable from "~/components/table/records/recordsTable.vue";
import ChartLayout from "~/components/layout/ChartLayout.vue";
import SearchByTerritoryType from "~/components/records/SearchByTerritoryType.vue";

const heroData = {
    title: "Records",
    description:
        "Tableau des stations météo ayant enregistrées un record de température sur une période donnée.",
};
</script>

<template>
    <UContainer>
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
