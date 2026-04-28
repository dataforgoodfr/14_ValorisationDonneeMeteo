<script setup lang="ts">
import Card from "../Card.vue";

const { yesterday, yesterdayLess365Days } = useCustomDate();

const { data: kpi } = useNationalIndicatorKpi(
    computed(() => ({
        date_start: dateToStringYMD(yesterdayLess365Days.value),
        date_end: dateToStringYMD(yesterday.value),
    })),
);

const { data: itnData } = useNationalIndicator(
    computed(() => ({
        date_start: dateToStringYMD(yesterdayLess365Days.value),
        date_end: dateToStringYMD(yesterday.value),
        granularity: "year" as const,
        slice_type: "full" as const,
    })),
);

const itnMean = computed(() => kpi.value?.itn_mean ?? null);
const deviationFromNormal = computed(
    () => kpi.value?.deviation_from_normal ?? null,
);

const itnColorClass = computed(() => {
    const point = itnData.value?.time_series[0];
    if (!point || itnMean.value == null) return "text-green-400";
    if (itnMean.value > point.baseline_std_dev_upper) return "text-red-400";
    if (itnMean.value < point.baseline_std_dev_lower) return "text-blue-400";
    return "text-green-400";
});

const itnDiff = computed(() => {
    if (kpi.value?.itn_mean == null || kpi.value.previous?.itn_mean == null)
        return null;
    return +(kpi.value.itn_mean - kpi.value.previous.itn_mean).toFixed(1);
});

const hotPeak = computed(() => kpi.value?.hot_peak_count ?? null);
const coldPeak = computed(() => kpi.value?.cold_peak_count ?? null);

const hotDiff = computed(() => {
    if (kpi.value == null) return null;
    return kpi.value.hot_peak_count - kpi.value.previous.hot_peak_count;
});

const coldDiff = computed(() => {
    if (kpi.value == null) return null;
    return kpi.value.cold_peak_count - kpi.value.previous.cold_peak_count;
});
</script>

<template>
    <div class="flex items-center flex-col gap-2">
        <div class="flex gap-40 items-start">
            <div class="w-fit">
                <Card title="" tooltip-text="" :show-title="false" transparent>
                    <template #kpi>
                        <p
                            class="font-semibold text-4xl mb-1"
                            :class="itnColorClass"
                        >
                            <span v-if="itnMean != null"
                                >{{ itnMean.toFixed(1) }} °C</span
                            >
                            <span v-else class="text-muted">—</span>
                        </p>
                    </template>
                    <template
                        v-if="deviationFromNormal != null"
                        #kpi-context-box
                    >
                        {{ deviationFromNormal >= 0 ? "+" : ""
                        }}{{ deviationFromNormal.toFixed(1) }}°C vs normale
                        1991-2020
                    </template>
                    <template #kpi-context-text>
                        en moyenne les 365 derniers jours
                    </template>
                    <template v-if="itnDiff != null" #variation>
                        <UIcon
                            :name="
                                itnDiff < 0
                                    ? 'i-lucide-arrow-down-right'
                                    : 'i-lucide-arrow-up-right'
                            "
                            :class="
                                itnDiff < 0 ? 'text-blue-400' : 'text-red-400'
                            "
                            class="font-semibold"
                        />
                        <span
                            class="text-sm font-semibold"
                            :class="
                                itnDiff < 0 ? 'text-blue-400' : 'text-red-400'
                            "
                        >
                            {{ itnDiff >= 0 ? "+" : "" }}{{ itnDiff }}°C
                        </span>
                        vs. 365 jours précédents
                    </template>
                </Card>
            </div>
            <p
                v-if="itnMean != null"
                class="flex-1 text-m text-blue-700 dark:text-primary pb-2"
            >
                La température en France métropolitaine fut en moyenne de
                {{ itnMean.toFixed(1) }}°C ces 365 derniers jours
            </p>
        </div>

        <div class="flex gap-6">
            <div class="w-fit">
                <Card
                    title="Nombre de jours anormalement chauds"
                    tooltip-text="Nombre de jours parmi les 365 derniers jours, pour lesquels l'ITN est au-delà de l'écart-type de la période des normales 1991-2020"
                >
                    >
                    <template #kpi>
                        <p class="font-semibold text-4xl mb-1 text-red-400">
                            <span v-if="hotPeak != null">
                                {{ hotPeak }}
                                <span class="text-sm font-normal">jours</span>
                            </span>
                            <span v-else class="text-muted">—</span>
                        </p>
                    </template>
                    <template #kpi-context-text>
                        période des normales 1991-2020
                    </template>
                    <template v-if="hotDiff != null" #variation>
                        <UIcon
                            :name="
                                hotDiff < 0
                                    ? 'i-lucide-arrow-down-right'
                                    : 'i-lucide-arrow-up-right'
                            "
                            class="text-red-400 font-semibold"
                        />
                        <span class="text-sm font-semibold text-red-400">
                            {{ hotDiff >= 0 ? "+" : "" }}{{ hotDiff }} jours
                        </span>
                        vs. 365 jours précédents
                    </template>
                </Card>
            </div>

            <div class="w-fit">
                <Card
                    title="Nombre de jours anormalement froids"
                    tooltip-text="Nombre de jours parmi les 365 derniers jours, pour lesquels l'ITN est en-deçà de l'écart-type de la période des normales 1991-2020"
                >
                    <template #kpi>
                        <p class="font-semibold text-4xl mb-1 text-blue-400">
                            <span v-if="coldPeak != null">
                                {{ coldPeak }}
                                <span class="text-sm font-normal">jours</span>
                            </span>
                            <span v-else class="text-muted">—</span>
                        </p>
                    </template>
                    <template #kpi-context-text>
                        période des normales 1991-2020
                    </template>
                    <template v-if="coldDiff != null" #variation>
                        <UIcon
                            :name="
                                coldDiff < 0
                                    ? 'i-lucide-arrow-down-right'
                                    : 'i-lucide-arrow-up-right'
                            "
                            class="text-blue-400 font-semibold"
                        />
                        <span class="text-sm font-semibold text-blue-400">
                            {{ coldDiff >= 0 ? "+" : "" }}{{ coldDiff }} jours
                        </span>
                        vs. 365 jours précédents
                    </template>
                </Card>
            </div>
        </div>
    </div>
</template>
