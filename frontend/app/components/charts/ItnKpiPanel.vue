<template>
    <div class="flex flex-col gap-3 w-52 shrink-0 py-2">
        <Card
            v-for="i in 3"
            :key="i"
            title="ITN moyen"
            tooltip-text="Moyenne de l'Indicateur Thermique National sur la période sélectionnée."
        >
            <template #kpi>
                <p
                    class="font-semibold text-4xl mb-1"
                    :class="
                        (currentMean ?? 0) >= 0
                            ? 'text-red-400'
                            : 'text-blue-400'
                    "
                >
                    <span v-if="currentMean != null">
                        {{ currentMean >= 0 ? "+" : ""
                        }}{{ currentMean.toFixed(1) }} °C
                    </span>
                    <span v-else class="text-muted">—</span>
                </p>
            </template>
            <template v-if="diff != null" #variation>
                <span class="text-sm">
                    {{ diff >= 0 ? "+" : "" }}{{ diff.toFixed(1) }}°C
                </span>
                <UIcon
                    v-if="diff < 0"
                    name="i-lucide-arrow-down-right"
                    class="text-blue-400"
                />
                <UIcon
                    v-if="diff > 0"
                    name="i-lucide-arrow-up-right"
                    class="text-red-400"
                />
                vs période précédente
            </template>
        </Card>
    </div>
</template>

<script setup lang="ts">
import Card from "~/components/home/Card.vue";
import { useItnStore } from "~/stores/itnStore";
import { dateToStringYMD } from "#imports";
import type { NationalIndicatorParams } from "~/types/api";

const store = useItnStore();
const {
    itnData,
    pickedDateStart,
    pickedDateEnd,
    granularity,
    sliceType,
    month_of_year,
    day_of_month,
} = storeToRefs(store);

const prevYearParams = computed<NationalIndicatorParams>(() => {
    const start = new Date(pickedDateStart.value);
    const end = new Date(pickedDateEnd.value);
    start.setFullYear(start.getFullYear() - 1);
    end.setFullYear(end.getFullYear() - 1);
    return {
        date_start: dateToStringYMD(start),
        date_end: dateToStringYMD(end),
        granularity: granularity.value,
        slice_type: sliceType.value,
        month_of_year: month_of_year.value,
        day_of_month: day_of_month.value,
    };
});

const { data: prevYearData } = useNationalIndicator(prevYearParams);

function meanTemperature(
    timeSeries: { temperature: number }[] | undefined,
): number | null {
    if (!timeSeries?.length) return null;
    return (
        timeSeries.reduce((sum, p) => sum + p.temperature, 0) /
        timeSeries.length
    );
}

const currentMean = computed(() => meanTemperature(itnData.value?.time_series));
const prevMean = computed(() =>
    meanTemperature(prevYearData.value?.time_series),
);

const diff = computed(() => {
    if (currentMean.value == null || prevMean.value == null) return null;
    return currentMean.value - prevMean.value;
});
</script>
