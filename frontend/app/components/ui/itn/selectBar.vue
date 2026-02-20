<script setup lang="ts">
import ExportPng from "./ExportPng.vue";
import monthRangeDatePicker from "./monthRangeDatePicker.vue";

// Granularity Selection
const granularity = ref([
    { label: "Jour", value: "day", disabled: true },
    { label: "Mois", value: "month" },
    { label: "Année", value: "year", disabled: true },
]);
const granularityValue = ref("Mois");
</script>

<template>
    <div class="flex gap-6">
        <USelect v-model="granularityValue" :items="granularity" />
        <monthRangeDatePicker />
        <ExportPng />
    </div>
</template>
