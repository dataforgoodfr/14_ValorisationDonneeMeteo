<script setup lang="ts">
import PagesHero from "~/components/layout/PagesHero.vue";
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

const selectBarAdapter = useRecordsSelectBarAdapter();

const store = useRecordsTableStore();

const heroData = {
    title: "Records",
    description:
        "Les records de température correspondent aux valeurs extrêmes — maximales ou minimales — mesurées depuis la création d'une station disposant d'au moins 20 ans de données.",
};
</script>

<template>
    <UContainer class="flex flex-col gap-y-16">
        <PagesHero
            :title="heroData.title"
            :description="heroData.description"
        />
        <div class="flex gap-24 flex-col">
            <div class="flex flex-col gap-4 bg-elevated rounded-lg p-14">
                <div class="flex items-end gap-4">
                    <div class="flex flex-col gap-1">
                        <p class="text-sm text-muted">Période</p>
                        <USelect
                            v-model="store.periodSelection"
                            :items="periodOptions"
                        />
                    </div>
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
                    <div class="flex flex-col flex-1 min-w-0 gap-4">
                        <RecordsTable />
                    </div>
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
                    <div class="flex flex-col md:flex-row gap-4 px-3 py-2">
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
        </div>
    </UContainer>
</template>
