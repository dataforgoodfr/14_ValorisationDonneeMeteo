<template>
    <StationMap
        :stations="mappableStations"
        :color-config="DEVIATION_MAP_MONTHLY_COLORS"
        :tooltip-formatter="tooltipFormatter"
        legend-label="Température (°C)"
        aspect-ratio="1"
    />
</template>

<script setup lang="ts">
import type { DeviationMapParams, MappableStation } from "~/types/api";
import { DEVIATION_MAP_MONTHLY_COLORS } from "~/constants/colors";
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
    useTemperatureDeviationMap(params, "home-deviation-map");

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

watch(params, async () => await fetchStations(), { deep: true });
</script>
