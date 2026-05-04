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

const { data: yesterdayData } = useNationalIndicator(yesterdayParams, true);

const yesterdayTemperature = computed(() => {
    return yesterdayData.value?.time_series[0]?.temperature;
});
const gap = computed(() => {
    const result = yesterdayData.value?.time_series[0];
    return result ? result.temperature - result.baseline_mean : undefined;
});
</script>
<template>
    <Card
        :title="`ITN Hier -  ${yesterday?.toLocaleDateString('fr-FR', { dateStyle: 'long' })}`"
        :tooltip-text="'L\'Indicateur Thermique National correspond à la température moyenne mesurée en France Métropolitaine à partir de 30 stations définies par Météo-France.'"
    >
        <template #kpi>
            <p
                v-if="yesterdayTemperature"
                class="font-semibold text-4xl mb-1"
                :class="
                    (yesterdayTemperature ?? 0) <= 0
                        ? 'text-blue-600'
                        : 'text-red-450'
                "
            >
                {{ yesterdayTemperature?.toFixed(1) }} °C
            </p>
        </template>
        <template v-if="gap" #kpi-context-box>
            {{ gap != null && gap > 0 ? "+" : "" }}{{ gap?.toFixed(1) }}°C vs
            normale 1991-2020
        </template>
    </Card>
</template>
