<script setup lang="ts">
import DayPicker from "~/components/ui/commons/selectBar/dayPicker.vue";
import { useCustomDate } from "#imports";

const dateStart = defineModel<Date>("startDate");
const dateEnd = defineModel<Date>("endDate");

const dates = useCustomDate();

const presetOptions: { label: string; value: string }[] = [
    { label: "Hier", value: "yesterday" },
    { label: "7 derniers jours", value: "7d" },
    { label: "30 derniers jours", value: "30d" },
    { label: "90 derniers jours", value: "90d" },
    { label: "365 derniers jours", value: "365d" },
    { label: "Personnalisé", value: "custom" },
];

const preset = ref("30d");

const offsets: Record<string, number> = {
    yesterday: 0,
    "7d": 6,
    "30d": 29,
    "90d": 89,
    "365d": 364,
};

const applyPreset = (): void => {
    const offset = offsets[preset.value];

    if (offset === undefined || preset.value === "custom") {
        return;
    }

    const yesterday = new Date(dates.yesterday.value);
    const start = new Date(yesterday);

    start.setDate(start.getDate() - offset);
    dateStart.value = start;
    dateEnd.value = yesterday;
};

onMounted((): void => {
    applyPreset();
});
</script>

<template>
    <div class="flex items-center gap-2">
        <USelect
            v-model="preset"
            :items="presetOptions"
            class="w-48"
            @change="applyPreset"
        />
        <div
            :class="
                preset !== 'custom'
                    ? 'opacity-50 pointer-events-none select-none'
                    : ''
            "
        >
            <DayPicker
                v-model:start-date="dateStart"
                v-model:end-date="dateEnd"
                :min-date="dates.absoluteMinDataDate.value"
                :max-date="dates.yesterday.value"
            />
        </div>
    </div>
</template>
