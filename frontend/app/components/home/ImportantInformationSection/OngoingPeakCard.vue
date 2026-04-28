<script setup lang="ts">
import Card from "../Card.vue";
import { dateToStringYMD } from "~/utils/date";
import { useNationalIndicator } from "~/composables/useNationalIndicator";
import type {
    NationalIndicatorDataPoint,
    NationalIndicatorParams,
} from "~/types/api";

const { yesterday } = useCustomDate();

const dateStart = computed(() => {
    const d = new Date(yesterday.value);
    d.setDate(d.getDate() - 90);
    return d;
});

const params = computed<NationalIndicatorParams>(() => ({
    date_start: dateToStringYMD(dateStart.value),
    date_end: dateToStringYMD(yesterday.value),
    granularity: "day",
}));

const { data } = useNationalIndicator(params);

const series = computed(() => data.value?.time_series ?? []);

type PeakType = "hot" | "cold";

interface Streak {
    type: PeakType;
    count: number;
    avgDeviation: number;
}

function pointPeakType(p: NationalIndicatorDataPoint): PeakType | null {
    if (p.is_hot_peak) return "hot";
    if (p.is_cold_peak) return "cold";
    return null;
}

const currentStreak = computed((): Streak | null => {
    const pts = series.value;
    if (!pts.length) return null;
    const lastType = pointPeakType(pts[pts.length - 1]);
    if (!lastType) return null;

    let count = 0;
    let totalDev = 0;
    for (let i = pts.length - 1; i >= 0; i--) {
        if (pointPeakType(pts[i]) !== lastType) break;
        count++;
        totalDev += pts[i].temperature - pts[i].baseline_mean;
    }
    return { type: lastType, count, avgDeviation: totalDev / count };
});

function sign(n: number): string {
    return n >= 0 ? `+${n.toFixed(1)}` : n.toFixed(1);
}

const kpiColor = computed(() => {
    if (currentStreak.value?.type === "hot") return "text-red-450";
    if (currentStreak.value?.type === "cold") return "text-blue-600";
    return "text-muted";
});
</script>

<template>
    <Card
        title="Pic en cours"
        tooltip-text="Nombre de jours consécutifs de pic de chaleur ou de froid jusqu'à hier (température au-delà d'un écart-type de la normale)"
    >
        <template #kpi>
            <p class="font-semibold mb-1">
                <template v-if="currentStreak">
                    <span class="text-4xl" :class="kpiColor">
                        {{ currentStreak.count }}
                    </span>
                    <span class="text-xl text-muted"> jours</span>
                </template>
                <span v-else class="text-4xl text-muted">—</span>
            </p>
        </template>

        <template v-if="currentStreak" #kpi-context-box>
            consécutifs de pics de
            {{ currentStreak.type === "hot" ? "chaleur" : "froid" }}
        </template>

        <template #kpi-context-text>
            <template v-if="currentStreak">
                <span :class="kpiColor">
                    {{ sign(currentStreak.avgDeviation) }}°C
                </span>
                en moyenne depuis {{ currentStreak.count }} jours
            </template>
            <template v-else>Aucune anomalie récente</template>
        </template>
    </Card>
</template>
