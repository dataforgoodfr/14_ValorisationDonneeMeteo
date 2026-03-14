<script setup lang="ts">
import PagesHero from "~/components/layout/PagesHero.vue";
import StationTable from "~/components/ui/ecartNormale/stationTable.vue";

const heroData = {
    title: "Records",
    description:
        "Tableau des stations météo ayant enregistrées un record de température sur une période donnée.",
};
</script>

<!--
 Objectifs V0 :
 - A Réaliser : https://github.com/dataforgoodfr/14_ValorisationDonneeMeteo/issues/7
-->

<template>
    <UContainer>
        <PagesHero
            :title="heroData.title"
            :description="heroData.description"
        />
        <StationTable />
    </UContainer>
</template>
