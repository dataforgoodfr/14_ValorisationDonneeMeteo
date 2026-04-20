<template>
    <div class="flex flex-col gap-2 w-[500px] flex-shrink-0">
        <div class="flex flex-col gap-0.5">
            <div class="flex items-baseline gap-2">
                <span class="text-sm text-muted">Écart à la normale moyen</span>
                <span
                    v-if="nationalDeviation != null"
                    class="text-lg font-semibold"
                    :class="
                        nationalDeviation >= 0
                            ? 'text-red-400'
                            : 'text-blue-400'
                    "
                >
                    {{ nationalDeviation >= 0 ? "+" : ""
                    }}{{ nationalDeviation.toFixed(1) }} °C
                </span>
                <span v-else class="text-lg font-semibold text-muted">—</span>
            </div>
            <div class="text-xs text-muted">
                <span v-if="baseline"
                    >Période des normales : {{ baseline }}</span
                >
                <span v-if="baseline"> · </span>
                en France métropolitaine
            </div>
        </div>

        <StationMap
            :stations="mappableStations"
            :color-config="DEVIATION_MAP_COLORS"
            :tooltip-formatter="tooltipFormatter"
            legend-label="Écart à la normale (°C)"
        />
    </div>
</template>

<script setup lang="ts">
import type { DeviationMapParams, MappableStation } from "~/types/api";
import { DEVIATION_MAP_COLORS } from "~/constants/colors";
import { formatDeviationMapTooltip } from "~/components/map/tooltipFormatters/deviationMapTooltipFormatter";
import StationMap from "~/components/map/StationMap.vue";

const props = defineProps<{
    dateStart: string;
    dateEnd: string;
}>();

const params = computed<DeviationMapParams>(() => ({
    date_start: props.dateStart,
    date_end: props.dateEnd,
    limit: 99999,
}));

const { data: stationsData, execute: fetchStations } =
    useTemperatureDeviationMap(params, "deviation-map");

const nationalDeviation = computed(
    () => stationsData.value?.national.deviation_mean ?? null,
);

const baseline = computed(() => {
    const b = stationsData.value?.metadata.baseline;
    if (!b) return null;
    return b.replace("-", " – ");
});

const mappableStations = computed<MappableStation[]>(
    () =>
        stationsData.value?.stations.map((s) => ({
            lat: s.lat,
            lon: s.lon,
            station_name: s.station_name,
            value: s.deviation,
        })) ?? [],
);

const tooltipFormatter = (properties: {
    station_name: string;
    value: number;
    record_date: string | null;
    department: string | null;
}) => formatDeviationMapTooltip(properties.station_name, properties.value);

onMounted(async () => {
    await fetchStations();
});

watch(
    params,
    async () => {
        await fetchStations();
    },
    { deep: true },
);
</script>
