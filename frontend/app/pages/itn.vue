<!--
 Objectifs V0 :
 - A Réaliser : https://github.com/dataforgoodfr/14_ValorisationDonneeMeteo/issues/4
-->

<script setup lang="ts">
import CombinedChart from "~/components/charts/CombinedChart.vue";
import PagesHero from "~/components/layout/PagesHero.vue";
import SelectBar from "~/components/ui/itn/selectBar.vue";

const heroData = {
    title: "ITN",
    description:
        "L'Indicateur Thermique National est la température moyenne mesurée à l'échelle du pays (moyenne des températures minimales et maximales sur 30 stations météorologiques réparties de manière équilibrée en France).",
};

// TODO : uncomment below when "useNationalIndicator" is working
// const { data, status, error } = await useNationalIndicator(params);

// just testing that the frontend can reach the backend api
const config = useRuntimeConfig();
const {
    data: records,
    _pending,
    _error,
} = await useFetch(config.public.apiBase);

console.log("Données reçues :", records.value);
</script>

<template>
    <UContainer class="flex flex-col gap-y-16">
        <PagesHero
            :title="heroData.title"
            :description="heroData.description"
        />
        <div>
            <SelectBar />
            <CombinedChart />
        </div>
    </UContainer>
</template>
