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
import {
    useRecordsTableStore,
    periodOptions,
} from "~/stores/recordsTableStore";
import { recordsHeroData, recordsSections } from "~/data/docRecords";

const selectBarAdapter = useRecordsSelectBarAdapter();

const store = useRecordsTableStore();

const heroData = recordsHeroData;
const infoPanelSections = recordsSections;
</script>

<template>
    <UContainer class="flex flex-col gap-y-16">
        <PagesHero
            :title="heroData.title"
            :description="heroData.description"
        />

        <div class="flex flex-col gap-4 dark:bg-elevated rounded-lg px-3 py-2">
            <div class="flex items-center gap-1">
                <p class="text-sm font-medium">Période</p>
                <FieldInfo
                    text="Sélectionnez une période pour afficher les records mensuels ou saisonnier ou sur toute l'année"
                />
            </div>

            <div class="flex items-end gap-4">
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

            <hr class="border-accented" />

            <div class="flex flex-col md:flex-row items-start gap-8">
                <ClientOnly>
                    <RecordsMap />
                </ClientOnly>

                <RecordsTable />
            </div>
        </div>

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

        <InfoPanel :title="heroData.title" :sections="infoPanelSections" />
    </UContainer>
</template>
