<script setup lang="ts">
import type { CalendarDate } from "@internationalized/date";

const props = defineProps<{
  minDate: CalendarDate;
  granularityValue: string;
}>();

const dateRangeDaily = defineModel<{ start: CalendarDate; end: CalendarDate }>({
  required: true,
});

// converts a CalendarDate format to the "YYYY-MM" string format
function toMonthString(date: CalendarDate) {
  return `${date.year}-${String(date.month).padStart(2, "0")}`;
}

// parses "2025-03" back into a CalendarDate format
function fromMonthString(value: string, base: CalendarDate) {
  const [year, month] = value.split("-").map(Number);
  return base.set({ year, month });
}

// Month mode

const startMonthInput = computed({
  get: () => toMonthString(dateRangeDaily.value.start),
  set: (v: string) => {
    dateRangeDaily.value = {
      ...dateRangeDaily.value,
      start: fromMonthString(v, dateRangeDaily.value.start),
    };
  },
});

const endMonthInput = computed({
  get: () => toMonthString(dateRangeDaily.value.end),
  set: (v: string) => {
    dateRangeDaily.value = {
      ...dateRangeDaily.value,
      end: fromMonthString(v, dateRangeDaily.value.end),
    };
  },
});

const minMonthAttr = computed(() => toMonthString(props.minDate));

// Year mode
const currentYear = new Date().getFullYear();
const yearOptions = Array.from(
  { length: currentYear - props.minDate.year + 1 },
  (_, i) => currentYear - i,
);

const startYear = computed({
  get: () => dateRangeDaily.value.start.year,
  set: (y: number) => {
    dateRangeDaily.value = {
      ...dateRangeDaily.value,
      start: dateRangeDaily.value.start.set({ year: y }),
    };
  },
});

const endYear = computed({
  get: () => dateRangeDaily.value.end.year,
  set: (y: number) => {
    dateRangeDaily.value = {
      ...dateRangeDaily.value,
      end: dateRangeDaily.value.end.set({ year: y }),
    };
  },
});
</script>

<template>
  <template v-if="granularityValue === 'Mois'">
    <UInput v-model="startMonthInput" type="month" :min="minMonthAttr" />
    <span>—</span>
    <UInput v-model="endMonthInput" type="month" :min="minMonthAttr" />
  </template>

  <template v-if="granularityValue === 'Années'">
    <USelect v-model="startYear" :items="yearOptions" />
    <span>—</span>
    <USelect v-model="endYear" :items="yearOptions" />
  </template>
</template>
