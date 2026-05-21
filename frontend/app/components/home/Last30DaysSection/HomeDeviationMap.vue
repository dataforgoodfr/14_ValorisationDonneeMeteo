<template>
    <StationMap
        :stations="mappableStations"
        :color-config="DEVIATION_MAP_COLORS"
        :tooltip-formatter="tooltipFormatter"
        legend-label="Température (°C)"
        aspect-ratio="1"
        :fit-padding="{ top: 10, right: 10, bottom: 10, left: 10 }"
    />
</template>

<script setup lang="ts">
import type {
    DeviationMapParams,
    MappableStation,
    MapTooltipFormatter,
} from "~/types/api";
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

const tooltipFormatter: MapTooltipFormatter = (properties) =>
    formatDeviationMapTooltip(
        properties.station_name,
        properties.value,
        DEVIATION_MAP_COLORS.stops,
    );

onMounted(async () => {
    await fetchStations();
});

watch(params, async () => await fetchStations(), { deep: true });
</script>
