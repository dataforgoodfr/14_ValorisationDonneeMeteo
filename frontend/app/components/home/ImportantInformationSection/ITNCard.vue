<script setup lang="ts">
import type { NationalIndicatorParams } from "~/types/api";
import Card from "../Card.vue";

const { yesterday } = useCustomDate();

const yesterdayParams = computed<NationalIndicatorParams>(() => ({
    date_start: dateToStringYMD(yesterday.value),
    date_end: dateToStringYMD(yesterday.value),
    granularity: "day",
    slice_type: "full",
}));

const { data: yesterdayData, pending } = useNationalIndicator(
    yesterdayParams,
    true,
);

const yesterdayTemperature = computed(
    () => yesterdayData.value?.time_series[0]?.temperature,
);

const itnColorClass = computed(() => {
    const point = yesterdayData.value?.time_series[0];
    if (!point || yesterdayTemperature.value == null) return "text-green-400";
    if (yesterdayTemperature.value > point.baseline_std_dev_upper)
        return "text-red-400";
    if (yesterdayTemperature.value < point.baseline_std_dev_lower)
        return "text-blue-400";
    return "text-green-400";
});

const gap = computed(() => {
    const result = yesterdayData.value?.time_series[0];
    return result ? result.temperature - result.baseline_mean : undefined;
});
</script>
<template>
    <Card
        :loading="pending"
        :title="`ITN Hier -  ${yesterday?.toLocaleDateString('fr-FR', { dateStyle: 'long' })}`"
        :tooltip-text="'L\'Indicateur Thermique National correspond à la température moyenne mesurée en France Métropolitaine à partir de 30 stations définies par Météo-France.'"
    >
        <template #kpi>
            <p
                v-if="yesterdayTemperature"
                class="font-semibold text-4xl mb-1"
                :class="itnColorClass"
            >
                {{ yesterdayTemperature?.toFixed(1) }} °C
            </p>
        </template>
        <template #kpi-context-box>
            <template v-if="gap">
                {{ gap?.toFixed(1) === "0.0" ? "= " : gap > 0 ? "+" : ""
                }}{{
                    gap?.toFixed(1) === "0.0" ? "" : gap?.toFixed(1) + "°C "
                }}vs normales 1991-2020
            </template>
        </template>
    </Card>
</template>
