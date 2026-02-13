<script setup lang="ts">
const params = defineModel<{
  date_start: string
  date_end: string
  granularity: "day" | "month" | "year"
}>({ required: true })

const granularityOptions = [
  { label: "Jour", value: "day" },
  { label: "Mois", value: "month" },
  { label: "Année", value: "year" },
];

const inputType = computed(() => {
  if (params.value.granularity === "day") return "date";
  return "month";
});

const yearOptions = computed(() => {
  const years = []
  for (let y = 1990; y <= new Date().getFullYear(); y++) {
    years.push({ label: String(y), value: String(y) });
  }
  return years;
});
</script>

<template>
  <UFormField label="Granularité">
    <USelect v-model="params.granularity" :items="granularityOptions" />
  </UFormField>

  <UFormField label="Date de début">
    <USelect v-if="params.granularity === 'year'" v-model="params.date_start"
      :items="yearOptions.filter(y => y.value <= params.date_end)" />
    <UInput v-else v-model="params.date_start" :type="inputType" :max="params.date_end" />
  </UFormField>

  <UFormField label="Date de fin">
    <USelect v-if="params.granularity === 'year'" v-model="params.date_end"
      :items="yearOptions.filter(y => y.value >= params.date_start)" />
    <UInput v-else v-model="params.date_end" :type="inputType" :min="params.date_start" />
  </UFormField>
</template>
