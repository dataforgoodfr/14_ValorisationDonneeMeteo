<script setup lang="ts">
import { CalendarDate } from "@internationalized/date";
import monthYearRangeDatePicker from "./monthYearRangeDatePicker.vue";

// Granularity Selection
const granularity = ref(["Années", "Mois", "Jours"]);
const granularityValue = ref("Mois");

// Set the default date range. 12 months range. From today, back to last year on the same day.
const computedDateRange = computed(() => {
  const today = new Date();
  const aYearAgo = new Date();
  aYearAgo.setFullYear(today.getFullYear() - 1);

  return {
    startDate: [
      aYearAgo.getFullYear(),
      aYearAgo.getMonth() + 1,
      aYearAgo.getDate(),
    ] as const,
    endDate: [
      today.getFullYear(),
      today.getMonth() + 1,
      today.getDate(),
    ] as const,
  };
});

const dateRangeDaily = shallowRef({
  start: new CalendarDate(...computedDateRange.value.startDate),
  end: new CalendarDate(...computedDateRange.value.endDate),
});

// First date with data
const minDate = new CalendarDate(1946, 1, 1);
const inputDate = useTemplateRef("inputDate");
</script>

<template>
  <USelect v-model="granularityValue" :items="granularity" />

  <UInputDate
    v-if="granularityValue === 'Jours'"
    v-model="dateRangeDaily"
    range
    :min-value="minDate"
  >
    <template #trailing>
      <UPopover :reference="inputDate?.inputsRef[0]?.$el">
        <UButton
          color="neutral"
          variant="link"
          size="sm"
          icon="i-lucide-calendar"
          aria-label="Select a date range"
          class="px-0"
        />

        <template #content>
          <UCalendar
            v-model="dateRangeDaily"
            class="p-2"
            :number-of-months="2"
            range
          />
        </template>
      </UPopover>
    </template>
  </UInputDate>

  <monthYearRangeDatePicker
    v-else
    v-model="dateRangeDaily"
    :min-date="minDate"
    :granularity-value="granularityValue"
  />
</template>
