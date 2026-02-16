<script setup lang="ts">
import {
    CalendarDate,
    DateFormatter,
    getLocalTimeZone,
} from "@internationalized/date";

// Default dates on first page load
const formattedToday = computed(() => {
    const today = new Date();
    return new CalendarDate(today.getFullYear(), today.getMonth() + 1, 1);
});
const formattedLastYear = computed(() => {
    const today = new Date();
    return new CalendarDate(today.getFullYear() - 1, today.getMonth() + 1, 1);
});
const startMonth = shallowRef(formattedLastYear.value);
const endMonth = shallowRef(formattedToday.value);
// First date with meteo data
const minDataDate = new CalendarDate(2020, 1, 1);

const df = new DateFormatter("en-US", {
    year: "numeric",
    month: "long",
});

// Display only month and year
const monthYearDisplay = (date: CalendarDate) => {
    return df.format(date.toDate(getLocalTimeZone()));
};
</script>

<template>
    <div class="flex items-center gap-1">
        <UPopover>
            <UButton color="neutral" variant="outline">
                {{ monthYearDisplay(startMonth) }}
            </UButton>
            <template #content>
                <UCalendar
                    v-model="startMonth"
                    class="p-2"
                    :month-controls="true"
                    :year-controls="true"
                    :min-value="minDataDate"
                    :max-value="formattedToday"
                />
            </template>
        </UPopover>
        <UIcon name="i-lucide-arrow-right" />
        <UPopover>
            <UButton color="neutral" variant="outline">
                {{ monthYearDisplay(endMonth) }}
            </UButton>
            <template #content>
                <UCalendar
                    v-model="endMonth"
                    class="p-2"
                    :month-controls="true"
                    :year-controls="true"
                    :min-value="startMonth"
                    :max-value="formattedToday"
                />
            </template>
        </UPopover>
    </div>
</template>
