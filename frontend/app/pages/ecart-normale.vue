<script setup lang="ts">
import PagesHero from "~/components/layout/PagesHero.vue";
import Barchart from "~/components/charts/Barchart.vue";
import LineChart from "~/components/charts/LineChart.vue";
// import StationTable from "~/components/ui/ecartNormale/stationTable.vue";
import MapEcartNormaleClient from "~/components/charts/MapEcartNormale.vue";
import ExportMenu from "~/components/ui/commons/exportMenu.vue";

const heroData = {
    title: "Ecart à la normale",
    description:
        'L\'écart à la normale est la différence entre la moyenne des températures sur une période, et les températures normales. Les " normales " sont calculées sur 30 ans et mises à jour toutes les décennies.',
};

const items = ref(["Bar Chart", "Line Chart"]);
const value = ref("Bar Chart");
const chartName = "ecart_normale";
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
        <USelect v-model="value" :items="items" />
        <ExportMenu :chart="chartName" class="ml-auto" />
        <Barchart v-if="value === `Bar Chart`" />
        <LineChart v-if="value === `Line Chart`" />
        <MapEcartNormaleClient />
        <!-- <StationTable /> -->
    </UContainer>
</template>
