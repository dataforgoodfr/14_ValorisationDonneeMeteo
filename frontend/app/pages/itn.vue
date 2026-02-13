<!--
 Objectifs V0 :
 - A Réaliser : https://github.com/dataforgoodfr/14_ValorisationDonneeMeteo/issues/4
-->

<script setup lang="ts">
import CombinedChart from "~/components/charts/CombinedChart.vue";
import DateRange from "~/components/ui/DateRange.vue";


const params = ref({
  date_start: "1990-01-01",
  date_end: "2024-12-31",
  granularity: "day" as "day" | "month" | "year",
});

// TODO : uncomment below when "useNationalIndicator" is working
// const { data, status, error } = await useNationalIndicator(params);
</script>

<template>
  <UContainer>
    <h1>Page Indicateur Thermique National</h1>
    <div class="flex items-center justify-center py-12 gap-8">
      <DateRange v-model="params" />
    </div>
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

  </UContainer>
</template>
