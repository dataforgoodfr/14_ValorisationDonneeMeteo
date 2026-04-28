<script setup lang="ts">
import Card from "../Card.vue";
import { dateToStringYMD } from "~/utils/date";
import { useNationalIndicator } from "~/composables/useNationalIndicator";
import type { NationalIndicatorParams } from "~/types/api";

const { yesterday, absoluteMinDataDate } = useCustomDate();

const params = computed<NationalIndicatorParams>(() => ({
    date_start: dateToStringYMD(absoluteMinDataDate.value),
    date_end: dateToStringYMD(yesterday.value),
    granularity: "year",
    slice_type: "day_of_month",
    month_of_year: yesterday.value.getMonth() + 1,
    day_of_month: yesterday.value.getDate(),
}));

const { data } = useNationalIndicator(params);

const series = computed(() => data.value?.time_series ?? []);

const yesterdayEntry = computed(() =>
    series.value.length > 0 ? series.value[series.value.length - 1] : null,
);

const rank = computed(() => {
    if (!yesterdayEntry.value) return null;
    const temp = yesterdayEntry.value.temperature;
    const sorted = [...series.value].sort(
        (a, b) => b.temperature - a.temperature,
    );
    return sorted.findIndex((p) => p.temperature === temp) + 1;
});

const recordEntry = computed(() => {
    if (!series.value.length) return null;
    return series.value.reduce((best, p) =>
        p.temperature > best.temperature ? p : best,
    );
});

function toOrdinal(n: number): string {
    return n === 1 ? "1er" : `${n}ème`;
}

const yesterdayLabel = computed(() =>
    yesterday.value.toLocaleDateString("fr-FR", {
        day: "numeric",
        month: "long",
    }),
);
</script>

<template>
    <Card
        title="Rang"
        tooltip-text="Rang de la valeur ITN d'hier parmi tous les mêmes jours enregistrés depuis 1946"
    >
        <template #kpi>
            <p v-if="rank !== null" class="font-semibold mb-1">
                <span class="text-4xl">#{{ rank }}</span>
                <span class="text-xl text-muted">
                    / {{ series.length }} ans</span
                >
            </p>
            <p v-else class="text-4xl font-semibold text-muted mb-1">—</p>
        </template>
        <template #kpi-context-box>
            <template v-if="rank !== null">
                {{ toOrdinal(rank) }} {{ yesterdayLabel }} le plus chaud
            </template>
        </template>
        <template #kpi-context-text>
            <template v-if="recordEntry">
                Record absolu :
                {{
                    recordEntry.temperature.toLocaleString("fr-FR", {
                        minimumFractionDigits: 1,
                        maximumFractionDigits: 1,
                    })
                }}°C en {{ recordEntry.date.slice(0, 4) }}
            </template>
        </template>
    </Card>
</template>
