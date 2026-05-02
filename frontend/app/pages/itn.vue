<script setup lang="ts">
import ItnChart from "~/components/charts/ItnChart.vue";
import ItnKpiPanel from "~/components/charts/ItnKpiPanel.vue";
import ItnStationsSection from "~/components/itn/ItnStationsSection.vue";
import PagesHero from "~/components/layout/PagesHero.vue";
import SelectBar from "~/components/ui/commons/selectBar/selectBar.vue";
import ChartLayout from "~/components/layout/ChartLayout.vue";
import InfoPanel from "~/components/ui/commons/InfoPanel.vue";
import { useItnSelectBarAdapter } from "~/adapters/itnSelectBarAdapter";
import { itnHeroData, itnSections } from "~/data/docItn";

const selectBarAdapter = useItnSelectBarAdapter();

const heroData = itnHeroData;
const infoPanelSections = itnSections;
</script>

<template>
    <UContainer class="flex flex-col gap-y-16">
        <PagesHero
            :title="heroData.title"
            :description="heroData.description"
        />
        <ChartLayout>
            <template #select-bar>
                <SelectBar :adapter="selectBarAdapter" />
            </template>
            <template #chart>
                <div class="flex gap-4">
                    <div class="flex-1 min-w-0">
                        <ItnChart :adapter="selectBarAdapter" />
                    </div>
                    <ItnKpiPanel
                        v-if="selectBarAdapter.chartType?.value !== 'stacked'"
                    />
                </div>
            </template>
        </ChartLayout>
        <ItnStationsSection />
        <InfoPanel :title="heroData.title" :sections="infoPanelSections" />
    </UContainer>
</template>
