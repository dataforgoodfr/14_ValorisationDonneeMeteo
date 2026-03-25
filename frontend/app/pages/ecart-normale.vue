<script setup lang="ts">
import PagesHero from "~/components/layout/PagesHero.vue";
import ChartLayout from "~/components/layout/ChartLayout.vue";
import SearchStation from "~/components/ecartNormale/searchStation.vue";
import { useDeviationSelectBarAdapter } from "~/adapters/deviationSelectBarAdapter";
import SelectBar from "~/components/ui/commons/selectBar/selectBar.vue";
import DeviationChart from "~/components/charts/DeviationChart.vue";

const selectBarAdapter = useDeviationSelectBarAdapter();

const heroData = {
    title: "Ecart à la normale",
    description:
        'L\'écart à la normale est la différence entre la moyenne des températures sur une période, et les températures normales. Les " normales " sont calculées sur 30 ans et mises à jour toutes les décennies.',
};
</script>

<template>
    <UContainer class="flex flex-col gap-y-16">
        <PagesHero
            :title="heroData.title"
            :description="heroData.description"
        />
        <ChartLayout :has-sidebar="true">
            <template #select-bar>
                <SelectBar :adapter="selectBarAdapter" />
            </template>
            <template #sidebar>
                <SearchStation />
            </template>
            <template #chart>
                <DeviationChart :adapter="selectBarAdapter" class="px-3 py-2" />
            </template>
        </ChartLayout>
    </UContainer>
</template>
