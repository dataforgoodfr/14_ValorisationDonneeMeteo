<script setup lang="ts">
import type { NationalIndicatorParams } from "~/types/api";
import Card from "./card.vue";

const { yesterday } = useCustomDate();

const params = computed<NationalIndicatorParams>(() => {
    return {
        date_start: yesterday.value
            .toISOString()
            .substring(0, "YYYY-MM-DD".length),
        date_end: yesterday.value
            .toISOString()
            .substring(0, "YYYY-MM-DD".length),
        granularity: "day",
        slice_type: "full",
    };
});
const { data } = useNationalIndicator(params, true);
console.log("Data:", data.value);

const result = computed(() => {
    if (!data.value) return null;
    const value = data.value.time_series[0];
    return value !== undefined ? value : null;
});
console.log("Result:", result.value);
console.log("Yesterday:", yesterday.value);
const yesterdayLastYear = new Date(yesterday.value);
yesterdayLastYear.setFullYear(yesterdayLastYear.getFullYear() - 1);
</script>
<template>
    <h1>LES INFORMATIONS À RETENIR</h1>
    <div>
        <Card
            :title="`ITN Hier -  ${toValue(yesterday).toLocaleDateString('fr-FR', { dateStyle: 'long' })}`"
            :tooltip-text="'L\'Indicateur Thermique National correspond à la température moyenne mesurée en France Métropolitaine à partir de 30 stations définies par MétéoFrance.'"
        >
            <p
                class="font-semibold text-4xl"
                :class="{
                    high: result?.temperature ?? 0 >= 0,
                    low: result?.temperature ?? 0 < 0,
                }"
            >
                {{ result?.temperature.toFixed(1) }} °C
            </p>
            <template #context-content> +4,5°C vs normale 1991-2020 </template>
            <template #footer>
                <div class="flex items-center">
                    <UIcon
                        v-if="result?.temperature ?? 0 <= 0"
                        name="i-lucide-arrow-down-right"
                        class="low"
                    />
                    <UIcon v-else name="i-lucide-arrow-up-right" class="high" />
                    <span
                        >vs
                        {{
                            toValue(yesterdayLastYear).toLocaleDateString(
                                "fr-FR",
                                { dateStyle: "long" },
                            )
                        }}</span
                    >
                </div>
            </template>
        </Card>
    </div>
</template>
<style lang="css" scoped>
.high {
    color: #ff6467;
}
.low {
    color: #82c4e8;
}
</style>
