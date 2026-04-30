<script setup lang="ts">
import * as echarts from "echarts/core";
import langFR from "~/i18n/langFR.js";
import { deviationChartTooltipFormatter } from "~/components/charts/tooltipFormatters/deviationChartTooltipFormatter";
import { CHART_ATTRIBUTION_GRAPHIC } from "~/constants/chartAttribution";
import { useMapColors } from "~/constants/colors";
import { FONT_CHARTS } from "~/constants/fonts";
import type { TemperatureDeviationGraphParams } from "~/types/api";
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

const chartRef = shallowRef();
const mapColors = useMapColors();

const renderer = ref<"svg" | "canvas">("canvas");

const initOptions = computed(() => ({
    height: 600,
    locale: "FR",
    renderer: renderer.value,
}));
provide(INIT_OPTIONS_KEY, initOptions);

const today = new Date();
const firstDayCurrentMonth = new Date(today.getFullYear(), today.getMonth());
const firstDayCurrentMonthTwoYearsAgo = new Date(
    today.getFullYear() - 2,
    today.getMonth(),
);

const params = computed<TemperatureDeviationGraphParams>(() => ({
    date_start: dateToStringYMD(firstDayCurrentMonthTwoYearsAgo),
    date_end: dateToStringYMD(firstDayCurrentMonth),
    granularity: "month",
    include_national: true,
    slice_type: "full",
}));

const { data: deviationData, pending } = useTemperatureDeviationGraph(params);

const barOption = computed<ECOption>(() => {
    const data = deviationData.value;

    if (!data) return {};

    const nationalData = data.national.data;
    console.log("nationalData", nationalData);
    const plotAmountToDisplay = 1;

    const option: ECOption = {
        dataset: nationalData.map(() => ({
            dimensions: [
                "date",
                "deviation_positive",
                "deviation_negative",
                "station_id",
            ],
            source:
                nationalData?.map((p) => ({
                    date: p.date,
                    deviation_positive: p.deviation >= 0 ? p.deviation : null,
                    deviation_negative: p.deviation < 0 ? p.deviation : null,
                    station_id: "national",
                })) ?? [],
        })),
        grid: nationalData.map((_, index) => ({
            top: `${index * (100 / plotAmountToDisplay) + 3}%`,
            height: `${100 / plotAmountToDisplay - 10}%`,
            left: 30,
            right: 10,
            containLabel: true,
        })),
        xAxis: nationalData.map((_, index) => ({
            type: "time",
            gridIndex: index,
            axisTick: { show: false },
            nameLocation: "middle",
            nameGap: 25,
            nameTextStyle: {
                fontSize: FONT_CHARTS.axisName,
                fontWeight: "bold",
            },
            axisPointer: { type: "line", label: { show: false } },
        })),
        yAxis: nationalData.map((_, index) => ({
            type: "value",
            gridIndex: index,
            splitNumber: 3,
            name: "Écart à la normale (°C)",
            nameRotate: 90,
            nameLocation: "middle",
            nameGap: 40,
            nameTextStyle: {
                fontSize: FONT_CHARTS.axisName,
                fontWeight: "bold",
            },
            axisLabel: { fontSize: FONT_CHARTS.axis },
            splitLine: {
                lineStyle: { type: "dashed", color: mapColors.value.splitLine },
            },
        })),
        series: nationalData.flatMap((_, index) => [
            {
                name: "Écart positif",
                type: "bar",
                stack: `deviation-${index}`,
                datasetIndex: index,
                encode: { x: "date", y: "deviation_positive" },
                color: mapColors.value.hot,
                tooltip: { show: true },
                xAxisIndex: index,
                yAxisIndex: index,
            },
            {
                name: "Écart négatif",
                type: "bar",
                stack: `deviation-${index}`,
                datasetIndex: index,
                encode: { x: "date", y: "deviation_negative" },
                color: mapColors.value.cold,
                tooltip: { show: true },
                xAxisIndex: index,
                yAxisIndex: index,
            },
        ]),
        title: {
            text: "France Métropolitaine",
            right: "right",
            top: `0%`,
        },
        axisPointer: {
            link: [{ xAxisIndex: "all" }],
            label: { backgroundColor: "#3a5080" },
        },
        legend: { bottom: 0 },
        tooltip: {
            trigger: "axis",
            axisPointer: { type: "line" },
            formatter: (params) => {
                return deviationChartTooltipFormatter(params, "month", [
                    {
                        station_id: "national",
                        station_name: "France Métropolitaine",
                    },
                ]);
            },
        },
        dataZoom: [{ xAxisIndex: [0], type: "inside", minSpan: 20 }],
        graphic: CHART_ATTRIBUTION_GRAPHIC,
    };
    return option;
});
</script>
<template>
    <VChart
        :ref="chartRef"
        :key="`last2yearsDeviationChart`"
        :option="barOption"
        :update-options="{ notMerge: true }"
        :init-options="initOptions"
        :loading="pending"
        :loading-options="{ text: 'Chargement…', color: '#3b82f6' }"
        autoresize
        class="mt-5"
    />
</template>
