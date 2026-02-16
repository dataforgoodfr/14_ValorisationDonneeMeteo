<script setup lang="ts">
import InputMonthRangeDatePicker from "./InputMonthRangeDatePicker.vue";
import PopoverMonthRangeDatePicker from "./PopoverMonthRangeDatePicker.vue";
// Granularity Selection
const granularity = ref(["Mois"]);
const granularityValue = ref("Mois");
</script>

<template>
    <div class="flex gap-6">
        <USelect v-model="granularityValue" :items="granularity" />
        <InputMonthRangeDatePicker />
        <PopoverMonthRangeDatePicker />
    </div>
</template>
