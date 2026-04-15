<script setup lang="ts">
import * as echarts from "echarts/core";
import langFR from "~/i18n/langFR.js";
import type { TemperatureDeviationGraphResponse } from "~/types/api";
import type { SelectBarAdapter } from "~/components/ui/commons/selectBar/types";
import type { EChartsOption } from "echarts";
import { useDeviationStore } from "#imports";
import { CHART_ATTRIBUTION_GRAPHIC } from "~/constants/chartAttribution";
import { deviationChartTooltipFormatter } from "./tooltipFormatters/deviationChartTooltipFormatter";
import {
    DataZoomComponent,
    GraphicComponent,
    GridComponent,
    LegendComponent,
    TitleComponent,
    TooltipComponent,
    VisualMapComponent,
} from "echarts/components";
import { BarChart, HeatmapChart } from "echarts/charts";
import { UniversalTransition } from "echarts/features";
import { CanvasRenderer } from "echarts/renderers";
import { useDeviationCalendarOption } from "~/composables/useDeviationCalendarOption";
import { COLORS } from "~/constants/colors";

echarts.registerLocale("FR", langFR);
echarts.use([
    TitleComponent,
    TooltipComponent,
    GridComponent,
    BarChart,
    HeatmapChart,
    LegendComponent,
    DataZoomComponent,
    VisualMapComponent,
    UniversalTransition,
    CanvasRenderer,
    GraphicComponent,
]);

interface Props {
    adapter: SelectBarAdapter<TemperatureDeviationGraphResponse>;
}

const props = defineProps<Props>();

const deviationStore = useDeviationStore();
const { selectedStationsAndNational } = storeToRefs(useDeviationStore());

const isChartMounted = ref<boolean>(true);

const renderer = ref<"svg" | "canvas">("canvas");

const initOptions = computed(() => ({
    height: 600,
    locale: "FR",
    renderer: renderer.value,
}));
provide(INIT_OPTIONS_KEY, initOptions);

const barOption = computed<ECOption>(() => {
    const data = props.adapter.data.value;

    if (!data) return {};

    const stationsAndNational =
        deviationStore.stationsAndNationalFormatted(data);
    const plotAmountToDisplay = stationsAndNational.length || 1;

    return {
        dataset: stationsAndNational.map((stationOrNational) => ({
            dimensions: [
                "date",
                "deviation_positive",
                "deviation_negative",
                "station_id",
            ],
            source:
                stationOrNational?.data?.map((p) => ({
                    date: p.date,
                    deviation_positive: p.deviation >= 0 ? p.deviation : null,
                    deviation_negative: p.deviation < 0 ? p.deviation : null,
                    station_id: stationOrNational.station_id,
                })) ?? [],
        })),
        grid: stationsAndNational.map((_, index) => ({
            top: `${index * (100 / plotAmountToDisplay) + 3}%`,
            height: `${100 / plotAmountToDisplay - 10}%`,
            left: 30,
            right: 10,
            containLabel: true,
        })),
        xAxis: stationsAndNational.map((_, index) => ({
            type: "time",
            gridIndex: index,
            axisTick: { show: false },
            nameLocation: "middle",
            nameGap: 25,
            nameTextStyle: { fontSize: 11, fontWeight: "bold" },
            axisPointer: { type: "line", label: { show: false } },
        })),
        yAxis: stationsAndNational.map((_, index) => ({
            type: "value",
            gridIndex: index,
            splitNumber: 3,
            name: "Ecart à la normale (°C)",
            nameRotate: 90,
            nameLocation: "middle",
            nameGap: 40,
            nameTextStyle: { fontSize: 10, fontWeight: "bold" },
            axisLabel: { fontSize: 10 },
            splitLine: { lineStyle: { type: "dashed" } },
        })),
        series: stationsAndNational.flatMap((_, index) => [
            {
                name: "Ecart positif",
                type: "bar",
                stack: `deviation-${index}`,
                datasetIndex: index,
                encode: { x: "date", y: "deviation_positive" },
                color: COLORS.positive,
                tooltip: { show: true },
                xAxisIndex: index,
                yAxisIndex: index,
            },
            {
                name: "Ecart négatif",
                type: "bar",
                stack: `deviation-${index}`,
                datasetIndex: index,
                encode: { x: "date", y: "deviation_negative" },
                color: COLORS.negative,
                tooltip: { show: true },
                xAxisIndex: index,
                yAxisIndex: index,
            },
        ]),
        title: stationsAndNational.map((station, index) => ({
            text: getStationById(
                selectedStationsAndNational.value,
                station.station_id,
            )?.station_name,
            right: "right",
            top: `${index * (100 / plotAmountToDisplay)}%`,
        })),
        axisPointer: {
            link: [{ xAxisIndex: "all" }],
            label: { backgroundColor: "#3a5080" },
        },
        legend: { bottom: 0 },
        tooltip: {
            trigger: "axis",
            axisPointer: { type: "line" },
            formatter: (params) => {
                return deviationChartTooltipFormatter(
                    params,
                    props.adapter.granularity.value,
                    selectedStationsAndNational.value,
                );
            },
        },
        dataZoom: [{ xAxisIndex: "all", type: "inside", minSpan: 20 }],
        graphic: CHART_ATTRIBUTION_GRAPHIC,
    };
});

const calendarOption = computed<ECOption | EChartsOption>(() => {
    const data = props.adapter.data.value;

    if (!data) return {} as ECOption;

    return useDeviationCalendarOption(
        data,
        props.adapter.granularity.value,
        selectedStationsAndNational.value,
    );
});

const option = computed<ECOption | EChartsOption>(() =>
    props.adapter.chartType?.value === "calendar"
        ? calendarOption.value
        : barOption.value,
);
</script>

<template>
    <div class="h-full">
        <div
            v-if="!props.adapter.data.value"
            class="flex flex-col justify-center h-full items-center text-stone-400"
        >
            <p>Selectionnez au moins une station</p>
            <p>
                pour afficher ces écarts à la normale, pour la période
                sélectionnée.
            </p>
        </div>
        <div
            v-else-if="
                props.adapter.chartType?.value === 'calendar' &&
                props.adapter.granularity.value === 'day'
            "
            class="flex justify-center items-center h-full text-stone-400"
        >
            <p>
                Le calendrier n'est pas disponible en granularité journalière.
            </p>
        </div>
        <template v-else>
            <VChart
                v-if="isChartMounted"
                :ref="adapter.chartRef"
                :key="`${adapter.granularity.value}-${adapter.chartType?.value}`"
                :option="option"
                :update-options="{ notMerge: true }"
                :init-options="initOptions"
                :loading="adapter.pending.value"
                :loading-options="{ text: 'Chargement…', color: '#3b82f6' }"
                autoresize
            />
        </template>
    </div>
</template>
