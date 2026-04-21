<script setup lang="ts">
import PagesHero from "~/components/layout/PagesHero.vue";
import ChartLayout from "~/components/layout/ChartLayout.vue";
import SearchStation from "~/components/ecartNormale/searchStation.vue";
import { useDeviationSelectBarAdapter } from "~/adapters/deviationSelectBarAdapter";
import SelectBar from "~/components/ui/commons/selectBar/selectBar.vue";
import DeviationChart from "~/components/charts/DeviationChart.vue";
import DeviationTable from "~/components/table/deviation/DeviationTable.vue";
import DayPicker from "~/components/ui/commons/selectBar/dayPicker.vue";
import type { ChartType } from "~/components/ui/commons/selectBar/types";
import MapD3 from "~/components/map/MapD3.vue";
import { useDeviationTableStore } from "~/stores/deviationTableStore";
import { useCustomDate } from "~/composables/useCustomDate";

const selectBarAdapter = useDeviationSelectBarAdapter();
const chartType = computed<ChartType>(
    () => selectBarAdapter.chartType?.value ?? "bar",
);

const tableStore = useDeviationTableStore();
const { dateStart, dateEnd } = storeToRefs(tableStore);
const dates = useCustomDate();

const toISODate = (date: Date) => date.toISOString().substring(0, 10);
const mapDateStart = computed(() => toISODate(dateStart.value));
const mapDateEnd = computed(() => toISODate(dateEnd.value));

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

        <div class="flex flex-col gap-4">
            <DayPicker
                v-model:start-date="dateStart"
                v-model:end-date="dateEnd"
                :min-date="dates.absoluteMinDataDate.value"
                :max-date="dates.yesterday.value"
            />

            <hr class="border-accented" />

            <div class="flex flex-col md:flex-row items-start gap-8">
                <ClientOnly>
                    <MapD3 :date-start="mapDateStart" :date-end="mapDateEnd" />
                </ClientOnly>
                <div class="flex flex-col flex-1 min-w-0 gap-4">
                    <DeviationTable :show-filters="false" />
                </div>
            </div>
        </div>

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
