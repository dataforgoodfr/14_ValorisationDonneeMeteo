<script setup lang="ts">
import PagesHero from "~/components/layout/PagesHero.vue";
import Barchart from "~/components/charts/Barchart.vue";
import LineChart from "~/components/charts/LineChart.vue";
import MapEcartNormaleClient from "~/components/charts/MapEcartNormale.vue";
import SelectBar from "~/components/ui/commons/selectBar/selectBar.vue";
import { useDeviationSelectBarAdapter } from "~/adapters/deviationSelectBarAdapter";

const selectBarAdapter = useDeviationSelectBarAdapter();

const heroData = {
    title: "Ecart à la normale",
    description:
        'L\'écart à la normale est la différence entre la moyenne des températures sur une période, et les températures normales. Les " normales " sont calculées sur 30 ans et mises à jour toutes les décennies.',
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
        <SelectBar :adapter="selectBarAdapter" />
        <Barchart
            v-if="selectBarAdapter.chartType!.value === `bar`"
            :adapter="selectBarAdapter"
        />
        <LineChart
            v-if="selectBarAdapter.chartType!.value === `line`"
            :adapter="selectBarAdapter"
        />
        <MapEcartNormaleClient />
        <!-- <StationTable /> -->
    </UContainer>
</template>
