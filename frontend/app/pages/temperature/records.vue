<script setup lang="ts">
import PagesHero from "~/components/layout/PagesHero.vue";
import InfoPanel from "~/components/ui/commons/InfoPanel.vue";
import FieldInfo from "~/components/ui/commons/FieldInfo.vue";
import RecordsTable from "~/components/table/records/recordsTable.vue";
import ChartLayout from "~/components/layout/ChartLayout.vue";
import SearchByTerritoryType from "~/components/records/SearchByTerritoryType.vue";
import { useRecordsSelectBarAdapter } from "~/adapters/recordsSelectBarAdapter";
import RecordsChart from "~/components/charts/recordsChart.vue";
import RecordsKpiPanel from "~/components/charts/RecordsKpiPanel.vue";
import SelectBar from "~/components/ui/commons/selectBar/selectBar.vue";
import RecordsMap from "~/components/map/RecordsMap.vue";
import { useRecordsTableStore } from "~/stores/recordsTableStore";
import { useRecordsChartStore } from "~/stores/recordsChartStore";
import { recordsHeroData, recordsSections } from "~/data/docRecords";
import { EXPORT_BTN_UI } from "~/constants/tableUtils";
import type { FilterField } from "~/components/ui/commons/FilterBar.vue";

const recordsFilterFields: FilterField[] = [
    { id: "name", label: "Station", type: "string-async" },
    { id: "departement", label: "Département", type: "string" },
    {
        id: "record",
        label: "Température du record absolu",
        type: "number-range",
    },
    { id: "record_date", label: "Date du record absolu", type: "date-range" },
    { id: "classe", label: "Classe", type: "string" },
    { id: "altitude", label: "Altitude", type: "number-range" },
    {
        id: "date_de_creation",
        label: "Année de création",
        type: "number-range",
    },
];

const selectBarAdapter = useRecordsSelectBarAdapter();

const store = useRecordsTableStore();
const chartStore = useRecordsChartStore();
const route = useRoute();

const { today, yesterday, yesterdayLess30Days, yesterdayLess365Days } =
    useCustomDate();

const isLoading = ref<boolean>(true); // SSR rendering takes ~2s

onMounted(() => {
    isLoading.value = false;

    const preset = route.query.preset;
    const view = route.query.view;

    if (!preset) {
        store.dateStart = undefined;
        store.dateEnd = undefined;
        store.ordering = "";
        return;
    }

    store.ordering = "-recordDate";

    if (preset === "today") {
        store.dateStart = today.value;
        store.dateEnd = today.value;
    } else if (preset === "30d") {
        store.dateStart = yesterdayLess30Days.value;
        store.dateEnd = yesterday.value;
    } else if (preset === "365d") {
        const start = new Date(yesterday.value);
        start.setFullYear(start.getFullYear() - 1);
        store.dateStart = start;
        store.dateEnd = yesterday.value;
    }

    if (view === "scatter") {
        chartStore.setGranularity("day");
        chartStore.setChartType("scatter");
        chartStore.periodType = "month";
        chartStore.month = undefined;
        chartStore.recordKind = "historical";

        if (preset === "30d") {
            chartStore.pickedDateStart = yesterdayLess30Days.value;
            chartStore.pickedDateEnd = yesterday.value;
        } else if (preset === "365d") {
            chartStore.pickedDateStart = yesterdayLess365Days.value;
            chartStore.pickedDateEnd = yesterday.value;
        }
    }
});

const heroData = recordsHeroData;
const infoPanelSections = recordsSections;

function exportCSV() {
    if (!import.meta.client) return;

    downloadCSV(
        buildRecordsCsv(store.filteredRecords),
        useFormatFileName(
            `tableau-records-${store.typeRecords}`,
            store.periodSelection,
            "csv",
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

        <ChartLayout id="chart" :has-sidebar="true">
            <template #select-bar>
                <SelectBar :adapter="selectBarAdapter" />
            </template>
            <template #sidebar>
                <SearchByTerritoryType />
            </template>
            <template #chart>
                <div class="flex flex-col md:flex-row gap-4 px-3 py-2">
                    <div class="flex flex-col gap-4 flex-1">
                        <UTabs
                            v-model="selectBarAdapter.recordKind!.value"
                            :items="[
                                {
                                    label: 'Records battus',
                                    value: 'historical',
                                },
                                {
                                    label: 'Records absolus',
                                    value: 'absolute',
                                },
                            ]"
                            class="w-fit"
                        />
                        <div
                            v-if="isLoading"
                            class="flex items-center justify-center min-h-32"
                        >
                            <UIcon
                                name="i-lucide-loader-circle"
                                class="animate-spin text-3xl text-muted"
                            />
                        </div>
                        <RecordsChart v-else :adapter="selectBarAdapter" />
                    </div>
                    <RecordsKpiPanel :adapter="selectBarAdapter" />
                </div>
            </template>
        </ChartLayout>

        <div
            id="table"
            class="flex flex-col gap-4 dark:bg-elevated rounded-lg px-3 py-2"
        >
            <div class="flex flex-col">
                <div class="flex items-start gap-1">
                    <p class="text-sm font-medium">Période</p>
                    <FieldInfo
                        text="Sélectionnez une période pour afficher les records mensuels ou saisonnier ou sur toute l'année"
                    />
                </div>
                <div class="flex flex-col justify-between gap-2">
                    <div class="flex gap-2">
                        <USelect
                            v-model="store.periodSelection"
                            :items="periodOptions"
                        />

                        <UFieldGroup>
                            <UButton
                                :ui="{
                                    base:
                                        store.typeRecords === 'hot'
                                            ? 'bg-rose-200 text-rose-600 ring-1 ring-rose-300 pointer-events-none'
                                            : '',
                                }"
                                color="neutral"
                                variant="outline"
                                label="Chaud"
                                @click="store.typeRecords = 'hot'"
                            />
                            <UButton
                                :ui="{
                                    base:
                                        store.typeRecords === 'cold'
                                            ? 'bg-blue-200 text-blue-650! dark:text-blue-700! ring-1 ring-blue-300 pointer-events-none'
                                            : '',
                                }"
                                color="neutral"
                                variant="outline"
                                label="Froid"
                                @click="store.typeRecords = 'cold'"
                            />
                        </UFieldGroup>
                    </div>
                    <div
                        class="flex flex-col lg:flex-row justify-between flex-1 gap-2"
                    >
                        <TableFilterBar
                            :filter-fields="recordsFilterFields"
                            :filters="store.filters"
                            :static-options="store.staticOptions"
                            :set-filter="store.setFilter"
                            :clear-filter="store.clearFilter"
                        />

                        <UButton
                            class="self-start"
                            label="Exporter CSV"
                            icon="i-lucide-download"
                            :ui="EXPORT_BTN_UI"
                            :disabled="store.pending"
                            @click="exportCSV"
                        />
                    </div>
                </div>
            </div>

            <hr class="border-accented" />

            <div class="flex flex-col md:flex-row items-start gap-8">
                <ClientOnly>
                    <RecordsMap />
                </ClientOnly>

                <RecordsTable />
            </div>
        </div>

        <InfoPanel :title="heroData.title" :sections="infoPanelSections" />
    </UContainer>
</template>
