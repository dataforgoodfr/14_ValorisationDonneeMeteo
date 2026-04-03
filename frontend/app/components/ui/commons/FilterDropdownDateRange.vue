<script setup lang="ts">
import DayPicker from "./selectBar/dayPicker.vue";

const today = new Date();

defineProps<{
    /** Start of the selected date range. */
    startDate: Date | undefined;
    /** End of the selected date range. */
    endDate: Date | undefined;
    /** When true, shows the "Effacer" button. */
    hasFilter: boolean;
}>();

const emit = defineEmits<{
    "update:startDate": [date: Date | undefined];
    "update:endDate": [date: Date | undefined];
    clear: [];
}>();
</script>

<template>
    <div class="p-3 flex flex-col gap-3">
        <DayPicker
            :start-date="startDate"
            :end-date="endDate"
            :max-date="today"
            @update:start-date="emit('update:startDate', $event)"
            @update:end-date="emit('update:endDate', $event)"
        />
        <button
            v-if="hasFilter"
            class="text-xs text-error hover:underline text-left"
            @click="emit('clear')"
        >
            Effacer
        </button>
    </div>
</template>
