<!--
 Objectifs V0 :
 - A Réaliser : https://github.com/dataforgoodfr/14_ValorisationDonneeMeteo/issues/4
-->

<script setup lang="ts">
import CombinedChart from "~/components/charts/CombinedChart.vue";
import PagesHero from "~/components/layout/PagesHero.vue";

const heroData = {
    title: "ITN",
    description:
        "L'Indicateur Thermique National est la température moyenne mesurée à l'échelle du pays (moyenne des températures minimales et maximales sur 30 stations météorologiques réparties de manière équilibrée en France).",
};

// TODO : replace 'granularity' with dropdown; V0 is : 'Month' only, 'Day' and 'Year' disabled
// const params = ref({
//   date_start: "1990-01-01",
//   date_end: "2024-12-31",
//   granularity: "day" as const,
// });

// TODO : uncomment below when "useNationalIndicator" is working
// const { data, status, error } = await useNationalIndicator(params);
</script>

<template>
    <UContainer>
        <PagesHero
            :title="heroData.title"
            :description="heroData.description"
        />
        <CombinedChart />
    </UContainer>
</template>
