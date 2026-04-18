<script setup lang="ts">
import PagesHero from "~/components/layout/PagesHero.vue";
import ChartLayout from "~/components/layout/ChartLayout.vue";
import SearchStation from "~/components/ecartNormale/searchStation.vue";
import { useDeviationSelectBarAdapter } from "~/adapters/deviationSelectBarAdapter";
import SelectBar from "~/components/ui/commons/selectBar/selectBar.vue";
import DeviationChart from "~/components/charts/DeviationChart.vue";
import DeviationTable from "~/components/table/deviation/DeviationTable.vue";
import type { ChartType } from "~/components/ui/commons/selectBar/types";

const selectBarAdapter = useDeviationSelectBarAdapter();
const chartType = computed<ChartType>(
    () => selectBarAdapter.chartType?.value ?? "bar",
);

const heroData = {
    title: "Écart à la normale",
    description:
        "L'écart de température à la normale est définit comme la différence de la température moyenne sur une période donnée et la température moyenne de référence calculée sur la période 1991–2020 pour une durée équivalente",
};
</script>

<template>
    <UContainer class="flex flex-col gap-y-16">
        <PagesHero
            :title="heroData.title"
            :description="heroData.description"
        />
        <DeviationTable />
        <ChartLayout :has-sidebar="true">
            <template #select-bar>
                <SelectBar :adapter="selectBarAdapter" />
            </template>
            <template #sidebar>
                <SearchStation />
            </template>
            <template #chart>
                <ClientOnly>
                    <DeviationChart
                        :adapter="selectBarAdapter"
                        :chart-type="chartType"
                        class="px-3 py-2"
                    />
                </ClientOnly>
            </template>
        </ChartLayout>
    </UContainer>
</template>
