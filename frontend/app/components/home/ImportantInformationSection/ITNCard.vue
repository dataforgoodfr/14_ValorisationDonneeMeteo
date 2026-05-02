<script setup lang="ts">
import type { NationalIndicatorParams } from "~/types/api";
import Card from "../Card.vue";

const { yesterday, yesterdayLastYear } = useCustomDate();

// Yesterday data
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

// Yesterday last year data
const yesterdayLastYearParams = computed<NationalIndicatorParams>(() => ({
    date_start: dateToStringYMD(yesterdayLastYear.value),
    date_end: dateToStringYMD(yesterdayLastYear.value),
    granularity: "day",
    slice_type: "full",
}));

const { data: yesterdayLastYearData } = useNationalIndicator(
    yesterdayLastYearParams,
    true,
);

const yesterdayLastYearTemperature = computed(
    () => yesterdayLastYearData.value?.time_series[0]?.temperature,
);
const temperatureChangeYearOverYear = computed<number | undefined>(() => {
    if (
        typeof yesterdayTemperature.value !== "number" ||
        typeof yesterdayLastYearTemperature.value !== "number"
    ) {
        return undefined;
    }
    console.log(
        "yesterdayLastYearTemperature.value - yesterdayTemperature.value",
        yesterdayLastYearTemperature.value - yesterdayTemperature.value,
    );
    return yesterdayLastYearTemperature.value - yesterdayTemperature.value;
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
            {{ gap?.toFixed(1) }}°C vs normale 1991-2020
        </template>
        <template v-if="temperatureChangeYearOverYear !== 0" #variation>
            <UIcon
                v-if="(temperatureChangeYearOverYear ?? 0) < 0"
                name="i-lucide-arrow-down-right font-semibold"
                class="text-blue-600"
            />
            <UIcon
                v-if="(temperatureChangeYearOverYear ?? 0) > 0"
                name="i-lucide-arrow-up-right font-semibold"
                class="text-red-450"
            />
            <span
                class="text-sm font-semibold"
                :class="
                    (temperatureChangeYearOverYear ?? 0) <= 0
                        ? 'text-blue-600'
                        : 'text-red-450'
                "
            >
                {{ temperatureChangeYearOverYear?.toFixed(1) }}°C
            </span>
            vs
            {{
                toValue(yesterdayLastYear).toLocaleDateString("fr-FR", {
                    dateStyle: "long",
                })
            }}
        </template>
    </Card>
</template>
