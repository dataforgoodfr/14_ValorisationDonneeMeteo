<script setup lang="ts">
import ItnChart from "~/components/charts/ItnChart.vue";
import PagesHero from "~/components/layout/PagesHero.vue";
import SelectBar from "~/components/ui/commons/selectBar/selectBar.vue";
import ChartLayout from "~/components/layout/ChartLayout.vue";
import { useItnSelectBarAdapter } from "~/adapters/itnSelectBarAdapter";

const selectBarAdapter = useItnSelectBarAdapter();

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
                <SelectBar :adapter="selectBarAdapter" />
            </template>
            <template #chart>
                <ItnChart :adapter="selectBarAdapter" class="px-3 py-2" />
            </template>
        </ChartLayout>
    </UContainer>
</template>
