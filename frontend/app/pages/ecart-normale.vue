<script setup lang="ts">
import PagesHero from "~/components/layout/PagesHero.vue";
import Barchart from "~/components/charts/Barchart.vue";
import LineChart from "~/components/charts/LineChart.vue";

const heroData = {
    title: "Ecart à la normale",
    description:
        'L\'écart à la normale est la différence entre la moyenne des températures sur une période, et les températures normales. Les " normales " sont calculées sur 30 ans et mises à jour toutes les décennies.',
};

const items = ref(["Bar Chart", "Line Chart"]);
const value = ref("Bar Chart");
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
        <USelectMenu v-model="value" :items="items" />
        <Barchart v-if="value === `Bar Chart`" />
        <LineChart v-if="value === `Line Chart`" />
    </UContainer>
</template>
