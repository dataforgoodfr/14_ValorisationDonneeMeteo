<template>
    <div class="flex flex-col gap-2 lg:w-155 w-full shrink-0">
        <StationMap
            class="-mt-20"
            :stations="mappableStations"
            :color-config="DEVIATION_MAP_COLORS"
            :tooltip-formatter="tooltipFormatter"
            legend-label="Écart à la normale (°C)"
        />
    </div>
</template>

<script setup lang="ts">
import type { MappableStation, TemperatureDeviationParams } from "~/types/api";
import { DEVIATION_MAP_COLORS } from "~/constants/colors";
import { formatDeviationMapTooltip } from "~/components/map/tooltipFormatters/deviationMapTooltipFormatter";
import StationMap from "~/components/map/StationMap.vue";

const props = defineProps<{
    dateStart: string;
    dateEnd: string;
    params: TemperatureDeviationParams;
}>();

const queryParams = computed<TemperatureDeviationParams>(() => ({
    date_start: props.dateStart,
    date_end: props.dateEnd,
    station_ids: props.params.station_ids,
    station_search: props.params.station_search,
    departments: props.params.departments,
    regions: props.params.regions,
    deviation_min: props.params.deviation_min,
    deviation_max: props.params.deviation_max,
    classe_recente_min: props.params.classe_recente_min,
    classe_recente_max: props.params.classe_recente_max,
    date_de_creation_min: props.params.date_de_creation_min,
    date_de_creation_max: props.params.date_de_creation_max,
    limit: 99999,
    offset: 0,
}));

const { data: stationsData, execute: fetchStations } = useTemperatureDeviation(
    queryParams,
    true,
    true,
    "deviation-map",
);

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
    queryParams,
    async () => {
        await fetchStations();
    },
    { deep: true },
);
</script>
