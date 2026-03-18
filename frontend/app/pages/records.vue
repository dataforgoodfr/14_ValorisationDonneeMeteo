<script setup lang="ts">
import PagesHero from "~/components/layout/PagesHero.vue";
import RecordsTable from "~/components/table/records/recordsTable.vue";

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
        <RecordsTable />
    </UContainer>
</template>
