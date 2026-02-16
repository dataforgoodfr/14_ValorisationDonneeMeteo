<script setup lang="ts">
// Default dates on first page load
const today = new Date();
const lastYear = new Date();
lastYear.setFullYear(today.getFullYear() - 1);

function dateFormatter(dateToFormat: Date) {
    const formattedMonth = () =>
        dateToFormat.getMonth() + 1 < 10
            ? `0${dateToFormat.getMonth() + 1}`
            : dateToFormat.getMonth() + 1;
    return `${dateToFormat.getFullYear()}-${formattedMonth()}`;
}

const formattedToday = dateFormatter(today);

const startMonth = ref(dateFormatter(lastYear));
const endMonth = ref(formattedToday);
// First date with meteo data
const minDataDate = "1946-01";
</script>

<template>
    <span class="flex items-center gap-2">
        <UInput
            v-model="startMonth"
            type="month"
            placeholder="Date de début"
            icon="i-lucide-calendar"
            size="md"
            color="primary"
            :min="minDataDate"
            :max="formattedToday"
        />

        <UInput
            v-model="endMonth"
            type="month"
            placeholder="Date de fin"
            icon="i-lucide-calendar"
            size="md"
            color="primary"
            :min="startMonth"
            :max="formattedToday"
        />
    </span>
</template>
