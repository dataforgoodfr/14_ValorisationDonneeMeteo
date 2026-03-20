<!--
 Objectifs V0 :
 - A Réaliser : https://github.com/dataforgoodfr/14_ValorisationDonneeMeteo/issues/4
-->

<script setup lang="ts">
// import CombinedChart from "~/components/charts/CombinedChart.vue";
import ItnChart from "~/components/charts/ItnChart.vue";
import PagesHero from "~/components/layout/PagesHero.vue";
import SelectBar from "~/components/ui/itn/selectBar.vue";
import ChartLayout from "~/components/layout/ChartLayout.vue";

const heroData = {
    title: "ITN",
    description:
        "L'Indicateur Thermique National est la température moyenne mesurée à l'échelle du pays (moyenne des températures minimales et maximales sur 30 stations météorologiques réparties de manière équilibrée en France).",
};
</script>

<template>
    <UContainer class="flex flex-col gap-y-16">
        <PagesHero
            :title="heroData.title"
            :description="heroData.description"
        />
        <ChartLayout>
            <template #select-bar>
                <SelectBar />
            </template>
            <template #chart>
                <ItnChart class="px-3 py-2" />
            </template>
        </ChartLayout>
    </UContainer>
</template>
