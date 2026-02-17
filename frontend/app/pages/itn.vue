<!--
 Objectifs V0 :
 - A Réaliser : https://github.com/dataforgoodfr/14_ValorisationDonneeMeteo/issues/4
-->

<script setup lang="ts">
<<<<<<< feat/#56_GenerateMockupDataFile
import CombinedChart from "~/components/charts/CombinedChart.vue";
import PagesHero from "~/components/layout/PagesHero.vue";

const heroData = {
    title: "ITN",
    description:
        "L'Indicateur Thermique National est la température moyenne mesurée à l'échelle du pays (moyenne des températures minimales et maximales sur 30 stations météorologiques réparties de manière équilibrée en France).",
};
=======
import type { container } from "#build/ui";
import CombinedChart from "~/components/charts/CombinedChart.vue";
import PagesHero from "~/components/layout/PagesHero.vue";
import SelectBar from "~/components/ui/itn/selectBar.vue";
>>>>>>> main

const heroData = {
    title: "ITN",
    description:
        "L'Indicateur Thermique National est la température moyenne mesurée à l'échelle du pays (moyenne des températures minimales et maximales sur 30 stations météorologiques réparties de manière équilibrée en France).",
};

// TODO : uncomment below when "useNationalIndicator" is working
// const { data, status, error } = await useNationalIndicator(params);
</script>

<template>
<<<<<<< feat/#56_GenerateMockupDataFile
    <UContainer>
=======
    <UContainer class="flex flex-col gap-y-16">
>>>>>>> main
        <PagesHero
            :title="heroData.title"
            :description="heroData.description"
        />
<<<<<<< feat/#56_GenerateMockupDataFile
        <CombinedChart />
        <!-- TODO : Implement template below when API "useNationalIndicator" is ready-->
        <!-- <div
      v-if="status === 'pending'"
      class="flex items-center justify-center py-12"
    >
      <UIcon name="i-lucide-loader-circle" class="animate-spin size-6" />
      <span class="ml-2">Chargement des données...</span>
    </div>

    <UAlert
      v-else-if="error"
      color="error"
      title="Erreur de chargement"
      :description="error.message"
    />

    <CombinedChart
      v-else-if="data?.time_series"
      :time-series="data.time_series"
    /> -->
=======
        <div>
            <SelectBar />
            <CombinedChart />
        </div>
>>>>>>> main
    </UContainer>
</template>
