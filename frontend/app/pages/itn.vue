<!--
 Objectifs V0 :
 - A Réaliser : https://github.com/dataforgoodfr/14_ValorisationDonneeMeteo/issues/4
-->

<script setup lang="ts">
import CombinedChart from "~/components/charts/CombinedChart.vue";
import selectBar from "~/components/ui/itn/selectBar.vue";
</script>

<template>
    <UContainer>
        <h1>Page Indicateur Thermique National</h1>
        <selectBar />
        <CombinedChart />
    </UContainer>
</template>
