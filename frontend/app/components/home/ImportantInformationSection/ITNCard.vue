<script setup lang="ts">
import Card from "../Card.vue";

const { yesterdayTemperature, gap, temperatureChangeYearOverYear } =
    useHomeData();
const { yesterday, yesterdayLastYear } = useCustomDate();
</script>
<template>
    <Card
        :title="`ITN Hier -  ${yesterday?.toLocaleDateString('fr-FR', { dateStyle: 'long' })}`"
        :tooltip-text="'L\'Indicateur Thermique National correspond à la température moyenne mesurée en France Métropolitaine à partir de 30 stations définies par MétéoFrance.'"
    >
        <template #kpi>
            <p
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
        <template #kpi-context-box>
            {{ gap?.toFixed(1) }}°C vs normale 1991-2020
        </template>
        <template #variation>
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
