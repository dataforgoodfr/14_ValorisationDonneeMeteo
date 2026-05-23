<script setup lang="ts">
import Card from "../Card.vue";
import type {
    NationalIndicatorParams,
    NationalIndicatorResponse,
} from "~/types/api";

const { yesterday, yesterdayLess365Days } = useCustomDate();

const { apiFetch } = useApiClient();

const { data: kpi, pending: kpiPending } = useNationalIndicatorKpi(
    computed(() => ({
        date_start: dateToStringYMD(yesterdayLess365Days.value),
        date_end: dateToStringYMD(yesterday.value),
    })),
);

const { data: itnData, pending: itnPending } = useNationalIndicator(
    computed<NationalIndicatorParams>(() => ({
        date_start: dateToStringYMD(yesterdayLess365Days.value),
        date_end: dateToStringYMD(yesterday.value),
        granularity: "year",
        slice_type: "full",
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
    return kpi.value.itn_mean - kpi.value.previous.itn_mean;
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

const hotDiffColor = computed(() => {
    if (hotDiff.value == null || hotDiff.value === 0) return "";
    return hotDiff.value < 0 ? "text-blue-400" : "text-red-400";
});
const coldDiffColor = computed(() => {
    if (coldDiff.value == null || coldDiff.value === 0) return "";
    return coldDiff.value < 0 ? "text-red-400" : "text-blue-400";
});

async function exportInCsv(type: "hot" | "cold") {
    const itnDataForCsv = await apiFetch<NationalIndicatorResponse>(
        "/temperature/national-indicator",
        {
            query: {
                date_start: dateToStringYMD(yesterdayLess365Days.value),
                date_end: dateToStringYMD(yesterday.value),
                granularity: "day",
                slice_type: "full",
            },
        },
    );

    const label =
        type === "hot"
            ? "jours-excessivement-chauds"
            : "jours-excessivement-froids";
    const dateStart = dateToStringYMD(yesterdayLess365Days.value);
    const dateEnd = dateToStringYMD(yesterday.value);

    if (!itnDataForCsv) return;

    downloadCSV(
        buildItnCsv(itnDataForCsv.time_series, type),
        useFormatFileName(label, `${dateStart}_${dateEnd}`, "csv"),
    );
}
</script>

<template>
    <div class="flex items-center flex-col gap-4">
        <div class="flex gap-2 items-start flex-col md:flex-row md:gap-40">
            <div class="w-fit">
                <Card
                    :loading="itnPending"
                    title=""
                    tooltip-text=""
                    :show-title="false"
                    transparent
                >
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
                        {{
                            deviationFromNormal.toFixed(1) === "0.0"
                                ? "= "
                                : deviationFromNormal > 0
                                  ? "+"
                                  : ""
                        }}
                        {{
                            deviationFromNormal.toFixed(1) === "0.0"
                                ? ""
                                : deviationFromNormal.toFixed(1) + "°C "
                        }}vs normales 1991-2020
                    </template>
                    <template #kpi-context-text>
                        en moyenne ces 365 derniers jours
                    </template>
                    <template v-if="itnDiff != null" #variation>
                        <UIcon
                            v-if="itnDiff.toFixed(1) !== '0.0'"
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
                            >{{
                                itnDiff.toFixed(1) !== "0.0"
                                    ? (itnDiff > 0 ? "+" : "") +
                                      itnDiff.toFixed(1) +
                                      "°C"
                                    : "="
                            }}
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

        <div class="flex gap-6 flex-col md:flex-row">
            <div class="w-fit">
                <Card
                    :loading="kpiPending"
                    title="Nombre de jours excessivement chauds"
                    tooltip-text="Nombre de jours parmi ces 365 derniers jours, pour lesquels l'ITN est au-delà de l'écart-type de la période des normales 1991-2020"
                    export-button-title="Exporter la liste des jours excessivement chauds"
                    @export="exportInCsv('hot')"
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
                        période des normales: 1991-2020
                    </template>
                    <template v-if="hotDiff != null" #variation>
                        <UIcon
                            v-if="hotDiff !== 0"
                            :name="
                                hotDiff < 0
                                    ? 'i-lucide-arrow-down-right'
                                    : 'i-lucide-arrow-up-right'
                            "
                            :class="hotDiffColor"
                            class="font-semibold"
                        />
                        <span
                            v-if="hotDiff !== 0"
                            class="text-sm font-semibold"
                            :class="hotDiffColor"
                        >
                            {{ hotDiff > 0 ? "+" : "" }}{{ hotDiff }} jours
                        </span>
                        <span
                            v-else
                            class="text-sm font-semibold"
                            :class="hotDiffColor"
                            >=</span
                        >
                        vs. 365 jours précédents
                    </template>
                </Card>
            </div>

            <div class="w-fit">
                <Card
                    :loading="kpiPending"
                    title="Nombre de jours excessivement froids"
                    tooltip-text="Nombre de jours parmi ces 365 derniers jours, pour lesquels l'ITN est en-deçà de l'écart-type de la période des normales 1991-2020"
                    export-button-title="Exporter la liste des jours excessivement froids"
                    @export="exportInCsv('cold')"
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
                        période des normales: 1991-2020
                    </template>
                    <template v-if="coldDiff != null" #variation>
                        <UIcon
                            v-if="coldDiff !== 0"
                            :name="
                                coldDiff < 0
                                    ? 'i-lucide-arrow-down-right'
                                    : 'i-lucide-arrow-up-right'
                            "
                            :class="coldDiffColor"
                            class="font-semibold"
                        />
                        <span
                            v-if="coldDiff !== 0"
                            class="text-sm font-semibold"
                            :class="coldDiffColor"
                        >
                            {{ coldDiff > 0 ? "+" : "" }}{{ coldDiff }} jours
                        </span>
                        <span
                            v-else
                            class="text-sm font-semibold"
                            :class="coldDiffColor"
                            >=</span
                        >
                        vs. 365 jours précédents
                    </template>
                </Card>
            </div>
        </div>
    </div>
</template>
