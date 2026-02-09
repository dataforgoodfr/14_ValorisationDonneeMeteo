<script setup lang="ts">
import Barchart from "~/components/charts/Barchart.vue";
import LineChart from "~/components/charts/LineChart.vue";

const items = ref(["Bar Chart", "Line Chart"]);
const value = ref("Bar Chart");
</script>

<!-- 
 Objectifs V0 :
 - A Réaliser : https://github.com/dataforgoodfr/14_ValorisationDonneeMeteo/issues/7
-->

<template>
  <UContainer>
    <h1 class="my-8">Page Ecart de température à la normale</h1>
    <USelectMenu v-model="value" :items="items" />
    <Barchart v-if="value === `Bar Chart`" />
    <LineChart v-if="value === `Line Chart`" />
  </UContainer>
</template>
