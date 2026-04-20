<script setup lang="ts">
import Card from "./Card.vue";

const {
    yesterday,
    yesterdayTemperature,
    gap,
    yesterdayLastYear,
    temperatureChangeYearOverYear,
} = useHomeData();
</script>
<template>
    <h3>LES INFORMATIONS À RETENIR</h3>

    <Card
        :title="`ITN Hier -  ${yesterday?.toLocaleDateString('fr-FR', { dateStyle: 'long' })}`"
        :tooltip-text="'L\'Indicateur Thermique National correspond à la température moyenne mesurée en France Métropolitaine à partir de 30 stations définies par MétéoFrance.'"
    >
        <template #kpi>
            <p
                class="font-semibold text-4xl mb-1"
                :class="{
                    red: yesterdayTemperature ?? 0 >= 0,
                    blue: yesterdayTemperature ?? 0 < 0,
                }"
            >
                {{ yesterdayTemperature?.toFixed(1) }} °C
            </p>
        </template>
        <template v-if="gap" #kpi-context-box>
            {{ gap.toFixed(1) }}°C vs normale 1991-2020
        </template>
        <template v-if="temperatureChangeYearOverYear" #variation>
            <span class="text-sm">
                {{ temperatureChangeYearOverYear.toFixed(1) }}°C
            </span>
            <UIcon
                v-if="temperatureChangeYearOverYear < 0"
                name="i-lucide-arrow-down-right"
                class="blue"
            />
            <UIcon
                v-if="temperatureChangeYearOverYear > 0"
                name="i-lucide-arrow-up-right"
                class="red"
            />
            vs
            {{
                toValue(yesterdayLastYear).toLocaleDateString("fr-FR", {
                    dateStyle: "long",
                })
            }}
        </template>
    </Card>
</template>
<style lang="css" scoped>
.red {
    color: #ff6467;
}
.blue {
    color: #82c4e8;
}
</style>
