<script setup lang="ts">
import PagesHero from "~/components/layout/PagesHero.vue";
import ChartLayout from "~/components/layout/ChartLayout.vue";
import InfoPanel from "~/components/ui/commons/InfoPanel.vue";
import type { InfoSection } from "~/types/common";
import SearchStation from "~/components/ecartNormale/searchStation.vue";
import { useDeviationSelectBarAdapter } from "~/adapters/deviationSelectBarAdapter";
import SelectBar from "~/components/ui/commons/selectBar/selectBar.vue";
import DeviationChart from "~/components/charts/DeviationChart.vue";
import DeviationTable from "~/components/table/deviation/DeviationTable.vue";
import DatePresetPicker from "~/components/ui/commons/DatePresetPicker.vue";
import type { ChartType } from "~/components/ui/commons/selectBar/types";
import MapD3 from "~/components/map/MapD3.vue";
import DeviationKpiPanel from "~/components/charts/DeviationKpiPanel.vue";
import { useDeviationTableStore } from "~/stores/deviationTableStore";

const selectBarAdapter = useDeviationSelectBarAdapter();
const chartType = computed<ChartType>(
    () => selectBarAdapter.chartType?.value ?? "bar",
);

const tableStore = useDeviationTableStore();
const { dateStart, dateEnd } = storeToRefs(tableStore);

const toISODate = (date: Date) => date.toISOString().substring(0, 10);
const mapDateStart = computed(() => toISODate(dateStart.value));
const mapDateEnd = computed(() => toISODate(dateEnd.value));

const heroData = {
    title: "Écart à la normale",
    description:
        "L'écart de température à la normale est définit comme la différence de la température moyenne sur une période donnée et la température moyenne de référence calculée sur la période 1991–2020 pour une durée équivalente",
};

const infoPanelSections: InfoSection[] = [
    {
        label: "Définition",
        content:
            "Les normales climatiques correspondent à des valeurs statistiques calculées" +
            " sur une période de référence de 30 ans. Celles-ci servent de point de comparaison" +
            " pour analyser le climat actuel et le changement climatique." +
            "\n(https://meteofrance.com/, https://fr.wikipedia.org/wiki/Normale_climatique)" +
            "\n\nL'écart de température à la normale est alors la différence entre la température" +
            " moyenne sur une période donnée et les normales climatiques.",
    },
    {
        label: "Méthode de calcul",
        content: [
            {
                title: "Écart à la normale quotidien en France métropolitaine",
                text:
                    "L'écart de température à la normale en France métropolitaine calculé chaque jour" +
                    " est la différence entre la valeur de l'Indicateur thermique National (ITN) mesurée ce jour" +
                    " et la valeur de l'ITN moyennée sur 30 ans ce même jour de l'année",
            },
            {
                title: "Écart à la normale quotidien d'une station",
                text:
                    "L'écart de température à la normale d'une station calculé chaque jour" +
                    " est la différence entre la température moyenne TNTXM de la station mesurée ce jour" +
                    " et la valeur de la température moyenne TNTXM de la station moyennée sur 30 ans ce" +
                    " même jour de l'année",
            },
            {
                title: "Écart à la normale mensuel/annuel ",
                text:
                    "Les normales mensuelles/annuelles sont calculées en moyennant les normales" +
                    " quotidennes pour chaque mois/année",
            },
        ],
    },
    {
        label: "Stations éligibles",
        content:
            "Le calcul des normales ne peut s’effectuer que si le nombre de données manquantes n’est pas" +
            " supérieur à celui préconisé par la norme OMM (https://donneespubliques.meteofrance.fr/client/document/normales-methode_299.pdf)" +
            "\n\nAinsi, pour qu'une station soit éligible au calcul d'un écart à la normale en considérant" +
            " la période 1991-2020 comme période des normales aux année et apparaisse sur le site dataclimat.fr," +
            " cette station doit avoir au moins 24 ans de données entre 1991-2020 et avoir une classe de qualité" +
            " de mesure de température définie par MéteoFrance entre 1 et 4.",
    },
    {
        label: "Sources",
        content:
            "- Les données sont issues de mesures open source de Meteo France" +
            "\n- Informations sur les normales climatiques: https://donneespubliques.meteofrance.fr/client/document/normales-methode_299.pdf)" +
            " https://meteofrance.com/, https://fr.wikipedia.org/wiki/Normale_climatique)" +
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

        <div class="flex flex-col gap-4 dark:bg-elevated rounded-lg p-14">
            <DatePresetPicker
                v-model:start-date="dateStart"
                v-model:end-date="dateEnd"
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

        <InfoPanel :title="heroData.title" :sections="infoPanelSections" />
    </UContainer>
</template>
