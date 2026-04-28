<script setup lang="ts">
import PagesHero from "~/components/layout/PagesHero.vue";
import InfoPanel from "~/components/ui/commons/InfoPanel.vue";
import type { InfoSection } from "~/types/common";
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

const selectBarAdapter = useRecordsSelectBarAdapter();

const store = useRecordsTableStore();

const heroData = {
    title: "Records",
    description:
        "Les records de température correspondent aux valeurs extrêmes — maximales ou minimales — mesurées depuis la création d'une station disposant d'au moins 20 ans de données.",
};

const infoPanelSections: InfoSection[] = [
    {
        label: "Définition",
        content:
            "Une mesure de température est un record si c'est la valeur la plus extrême" +
            " (chaude ou froide) jamais mesurée, à date, sur la période d'analyse sélectionnée.",
    },
    {
        label: "Méthode de calcul",
        content: [
            {
                title: "Records absolus",
                text:
                    "Un records absolu est la (et l'unique) valeur de température la plus extrême jamais" +
                    " mesurée sur la période d'anlyse sélectionnée",
            },
            {
                title: "Records battus",
                text:
                    "Les records battus sont la liste des records qu'une station ou une région a connu" +
                    " au cours du temps. Chaque record battu fut un record absolu sur la période sélectionné" +
                    " à sa date du record, mais il existe plusieurs records battus qui ne sont plusieurs des records" +
                    " absolu: le record absolu d'une station ou d'une région est en fait le dernier record battu.",
            },
            {
                title: "Période d'analyse",
                text:
                    "La période d'anlayse permet d'afficher les records battus ou absolus sur une partie de l'année seulement." +
                    "Si la période d'anlayse est un mois, les records mensuels du mois sélectionné sont affichés," +
                    " si la période d'anlayse est une saison, les records de saison sont affichés. Si la période est" +
                    " 'Période complète' les records tous mois confondus sont affichés.",
            },
        ],
    },
    {
        label: "Stations éligibles",
        content:
            "Pour être pertinent un record ne peut être déclaré comme tel que si la station a au moins 20 dans de données et si" +
            " sa classe de qualité de mesure de température définie par MéteoFrance est comprise entre 1 et 3.",
    },
    {
        label: "Sources",
        content:
            "- Les données sont issues de mesures open source de Meteo France" +
            "\n- Classe des stations: https://www.data.gouv.fr/datasets/fiches-dinformations-sur-les-stations",
    },
];
</script>

<template>
    <UContainer class="flex flex-col gap-y-16">
        <PagesHero
            :title="heroData.title"
            :description="heroData.description"
        />
        <div class="flex gap-24 flex-col">
            <div class="flex flex-col gap-4 dark:bg-elevated rounded-lg p-14">
                <div class="flex items-end gap-4">
                    <div class="flex flex-col gap-1">
                        <div class="flex items-center gap-1">
                            <p class="text-sm text-muted">Période</p>
                            <FieldInfo
                                text="Sélectionnez une période pour afficher les records mensuels ou saisonnier ou sur toute l'année"
                            />
                        </div>
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

        <InfoPanel :title="heroData.title" :sections="infoPanelSections" />
    </UContainer>
</template>
