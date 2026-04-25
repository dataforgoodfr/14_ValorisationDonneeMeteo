<template>
    <div
        class="flex flex-col items-center justify-center gap-2 w-[500px] flex-shrink-0"
    >
        <div class="flex flex-col gap-0.5">
            <div class="flex items-baseline gap-2">
                <Card
                    title="Ecart à la normale en France"
                    tooltip-text="Ecart à la normale moyen en France métropolitaine sur la période sélectionnée."
                >
                    <template #kpi>
                        <p class="font-semibold text-4xl mb-1 text-red-400">
                            <span v-if="kpi?.deviation_from_normal != null"
                                ><span
                                    >{{
                                        kpi.deviation_from_normal >= 0
                                            ? "+"
                                            : ""
                                    }}{{ kpi.deviation_from_normal.toFixed(1) }}
                                    °C
                                </span>
                            </span>
                            <span v-else class="text-muted">—</span>
                        </p>
                    </template>
                    <template #kpi-context-text>
                        période des normales: 1991-2020
                    </template>
                </Card>
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
import type {
    DeviationMapParams,
    MappableStation,
    NationalIndicatorKpiParams,
} from "~/types/api";
import { DEVIATION_MAP_COLORS } from "~/constants/colors";
import { formatDeviationMapTooltip } from "~/components/map/tooltipFormatters/deviationMapTooltipFormatter";
import StationMap from "~/components/map/StationMap.vue";
import Card from "~/components/home/Card.vue";
import { dateToStringYMD } from "#imports";

const props = defineProps<{
    dateStart: string;
    dateEnd: string;
}>();

const paramsItn = computed<NationalIndicatorKpiParams>(() => ({
    date_start: dateToStringYMD(new Date(props.dateStart)),
    date_end: dateToStringYMD(new Date(props.dateEnd)),
}));

const { data: kpi } = useNationalIndicatorKpi(paramsItn);

const params = computed<DeviationMapParams>(() => ({
    date_start: props.dateStart,
    date_end: props.dateEnd,
    limit: 99999,
}));

const { data: stationsData, execute: fetchStations } =
    useTemperatureDeviationMap(params, "deviation-map");

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
