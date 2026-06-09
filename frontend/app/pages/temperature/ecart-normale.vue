<script setup lang="ts">
import PagesHero from "~/components/layout/PagesHero.vue";
import ChartLayout from "~/components/layout/ChartLayout.vue";
import InfoPanel from "~/components/ui/commons/InfoPanel.vue";
import SearchStation from "~/components/ecartNormale/searchStation.vue";
import { useDeviationSelectBarAdapter } from "~/adapters/deviationSelectBarAdapter";
import SelectBar from "~/components/ui/commons/selectBar/selectBar.vue";
import DeviationChart from "~/components/charts/DeviationChart.vue";
import DeviationTable from "~/components/table/deviation/DeviationTable.vue";
import type { ChartType } from "~/components/ui/commons/selectBar/types";
import MapD3 from "~/components/map/MapD3.vue";
import DeviationKpiPanel from "~/components/charts/DeviationKpiPanel.vue";
import { useDeviationTableStore } from "~/stores/deviationTableStore";
import {
    ecartNormaleHeroData,
    ecartNormaleSections,
} from "~/data/docEcartNormale";
import type { FilterField } from "~/components/ui/commons/FilterBar.vue";
import { buildDeviationCsv } from "~/utils/deviationCsv";
import type { TemperatureDeviationResponse } from "~/types/api";
import { EXPORT_BTN_UI } from "~/constants/tableUtils";
import DatePresetPicker from "~/components/ui/commons/DatePresetPicker.vue";
import TableFilterBar from "~/components/table/TableFilterBar.vue";

const deviationFilterFields: FilterField[] = [
    { id: "name", label: "Station", type: "string-async" },
    { id: "departement", label: "Département", type: "string" },
    { id: "region", label: "Région", type: "string" },
    {
        id: "deviation",
        label: "Écart à la normale",
        type: "number-range",
        unit: "°C",
    },
    {
        id: "temperatureMean",
        label: "Température moyenne",
        type: "number-range",
        unit: "°C",
    },
    { id: "classe", label: "Classe", type: "string" },
    { id: "anneeDeCreation", label: "Année de création", type: "number-range" },
];

const selectBarAdapter = useDeviationSelectBarAdapter();
const chartType = computed<ChartType>(
    () => selectBarAdapter.chartType?.value ?? "bar",
);

const tableStore = useDeviationTableStore();
const { dateStart, dateEnd, exportParams, pending } = storeToRefs(tableStore);

const { yesterday, yesterdayLess30Days } = useCustomDate();

onMounted(() => {
    tableStore.dateStart = yesterdayLess30Days.value;
    tableStore.dateEnd = yesterday.value;
});

const isPeriodInfoOpen = ref(false);

const toISODate = (date: Date) => date.toISOString().substring(0, 10);
const mapDateStart = computed(() => toISODate(dateStart.value));
const mapDateEnd = computed(() => toISODate(dateEnd.value));

const heroData = ecartNormaleHeroData;
const infoPanelSections = ecartNormaleSections;
const { apiFetch } = useApiClient();

async function exportCSV() {
    if (!import.meta.client) return;
    const data = await apiFetch<TemperatureDeviationResponse>(
        "/temperature/deviation",
        { query: { ...exportParams.value, limit: 9999 } },
    );

    downloadCSV(
        buildDeviationCsv(data.stations),
        useFormatFileName(
            "tableau-ecart-normale",
            "", // non utile pour deviation
            "csv",
            dateStart.value,
            dateEnd.value,
        ),
    );
}
</script>

<template>
    <UContainer class="flex flex-col gap-y-16">
        <PagesHero
            :title="heroData.title"
            :description="heroData.description"
        />

        <ChartLayout :has-sidebar="true" chart-height="md:h-170">
            <template #select-bar>
                <SelectBar :adapter="selectBarAdapter" />
            </template>
            <template #sidebar>
                <SearchStation />
            </template>
            <template #chart>
                <div
                    v-if="selectBarAdapter.pending.value"
                    class="flex items-center justify-center min-h-32"
                >
                    <UIcon
                        name="i-lucide-loader-circle"
                        class="animate-spin text-3xl text-muted"
                    />
                </div>
                <ClientOnly v-else>
                    <div class="flex flex-col md:flex-row gap-4">
                        <DeviationChart
                            :adapter="selectBarAdapter"
                            :chart-type="chartType"
                            class="flex-1"
                        />
                        <DeviationKpiPanel />
                    </div>
                </ClientOnly>
            </template>
        </ChartLayout>

        <div
            id="table"
            class="flex flex-col gap-4 dark:bg-elevated rounded-lg px-3 py-2"
        >
            <div class="flex flex-col">
                <div class="flex items-center">
                    <p class="text-sm font-medium">
                        Période de moyennage des données
                    </p>
                    <UPopover v-model:open="isPeriodInfoOpen">
                        <button
                            class="text-blue-350 hover:text-blue-300 transition-colors cursor-pointer"
                            @mouseenter="isPeriodInfoOpen = true"
                            @mouseleave="isPeriodInfoOpen = false"
                        >
                            <UIcon name="i-lucide-circle-info" />
                        </button>
                        <template #content>
                            <p class="p-3 text-sm max-w-64">
                                Sélectionnez la période au cours de laquelle les
                                données de la carte et du tableau seront
                                moyennées
                            </p>
                        </template>
                    </UPopover>
                </div>

                <div class="flex flex-col justify-between gap-2">
                    <DatePresetPicker
                        v-model:start-date="dateStart"
                        v-model:end-date="dateEnd"
                    />
                    <div
                        class="flex flex-col lg:flex-row justify-between flex-1 gap-2"
                    >
                        <TableFilterBar
                            endpoint="/stations/deviation/"
                            :filter-fields="deviationFilterFields"
                            :filters="tableStore.filters"
                            :static-options="tableStore.staticOptions"
                            :set-filter="tableStore.setFilter"
                            :clear-filter="tableStore.clearFilter"
                        />

                        <UButton
                            class="self-start"
                            label="Exporter CSV"
                            icon="i-lucide-download"
                            :ui="EXPORT_BTN_UI"
                            :disabled="pending"
                            @click="exportCSV"
                        />
                    </div>
                </div>
            </div>

            <hr class="border-accented" />

            <div class="flex lg:flex-row flex-col items-start gap-8">
                <ClientOnly>
                    <MapD3
                        :date-start="mapDateStart"
                        :date-end="mapDateEnd"
                        :params="exportParams"
                    />
                </ClientOnly>

                <div class="w-full overflow-x-auto">
                    <DeviationTable :show-filters="false" />
                </div>
            </div>
        </div>

        <InfoPanel :title="heroData.title" :sections="infoPanelSections" />
    </UContainer>
</template>
