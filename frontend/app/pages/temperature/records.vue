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
import { recordsHeroData, recordsSections } from "~/data/docRecords";
import RecordsFilterBar from "~/components/table/records/RecordsFilterBar.vue";
import { EXPORT_BTN_UI } from "~/constants/tableUtils";

const selectBarAdapter = useRecordsSelectBarAdapter();

const store = useRecordsTableStore();
const route = useRoute();

const { today, yesterday, yesterdayLess30Days } = useCustomDate();

onMounted(() => {
    const preset = route.query.preset;
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

        <ChartLayout :has-sidebar="true">
            <template #select-bar>
                <SelectBar :adapter="selectBarAdapter" />
            </template>
            <template #sidebar>
                <SearchByTerritoryType />
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
                <div v-else class="flex flex-col md:flex-row gap-4 px-3 py-2">
                    <div class="flex flex-col gap-4 flex-1">
                        <UTabs
                            v-model="selectBarAdapter.recordKind!.value"
                            :items="[
                                {
                                    label: 'Records absolus',
                                    value: 'absolute',
                                },
                                {
                                    label: 'Records battus',
                                    value: 'historical',
                                },
                            ]"
                            class="w-fit"
                        />
                        <RecordsChart :adapter="selectBarAdapter" />
                    </div>
                    <RecordsKpiPanel :adapter="selectBarAdapter" />
                </div>
            </template>
        </ChartLayout>

        <div
            id="table"
            class="flex flex-col gap-4 dark:bg-elevated rounded-lg px-3 py-2"
        >
            <div class="flex items-center gap-1">
                <p class="text-sm font-medium">Période</p>
                <FieldInfo
                    text="Sélectionnez une période pour afficher les records mensuels ou saisonnier ou sur toute l'année"
                />
            </div>

            <div class="flex items-end gap-4">
                <div class="flex flex-col md:flex-row gap-4">
                    <RecordsFilterBar />
                    <div class="mt-3.5">
                        <UButton
                            label="Exporter CSV"
                            icon="i-lucide-download"
                            class="ml-auto"
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
