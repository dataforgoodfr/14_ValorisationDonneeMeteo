<script setup lang="ts">
import { KPI_SECONDARY_TEXT_CLASS } from "~/constants/tableUtils";

interface Props {
    type: "hot" | "cold";
}

const props = defineProps<Props>();

const { isHot, badgeClass, borderClass, icon, label } = useTemperatureTypeStyle(
    computed(() => props.type),
);

const { yesterday, yesterdayLess30Days } = useCustomDate();

const { data } = useTemperatureDeviation(
    computed(() => ({
        date_start: dateToStringYMD(yesterdayLess30Days.value),
        date_end: dateToStringYMD(yesterday.value),
        ordering: isHot.value ? "-deviation" : "deviation",
        limit: 1,
    })),
    undefined,
    false,
);

const station = computed(() => data.value?.stations[0] ?? null);
</script>

<template>
    <div class="rounded-xl border p-4 flex flex-col gap-3" :class="borderClass">
        <div
            class="w-fit flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold"
            :class="badgeClass"
        >
            <UIcon :name="icon" class="text-sm" />
            {{ label }}
        </div>

        <div v-if="station" class="flex items-center justify-between gap-8">
            <div class="flex items-start gap-2">
                <span class="text-xs" :class="KPI_SECONDARY_TEXT_CLASS"
                    >#1</span
                >
                <div>
                    <p class="font-semibold text-sm">
                        {{ station.station_name }}
                    </p>
                    <p class="text-xs" :class="KPI_SECONDARY_TEXT_CLASS">
                        {{ station.region }} · {{ station.department }}
                    </p>
                </div>
            </div>

            <div
                class="px-3 py-1.5 rounded-lg font-bold text-lg shrink-0"
                :class="badgeClass"
            >
                {{ station.deviation >= 0 ? "+" : ""
                }}{{ station.deviation.toFixed(1) }}°C
            </div>
        </div>

        <p v-else class="text-xs italic" :class="KPI_SECONDARY_TEXT_CLASS">
            Aucune donnée disponible sur cette période
        </p>
    </div>
</template>
