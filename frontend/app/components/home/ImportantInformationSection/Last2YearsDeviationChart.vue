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
    height: 250,
    locale: "FR",
    width: 600,
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

    const option: ECOption = {
        dataset: {
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
        },
        grid: {
            top: 3,
            height: "90%",
            left: 30,
            right: 10,
            containLabel: true,
        },
        xAxis: {
            type: "time",
            axisTick: { show: false },
            nameLocation: "middle",
            axisPointer: { type: "line", label: { show: false } },
        },
        yAxis: {
            type: "value",
            splitNumber: 3,
            name: "Écart à la normale (°C)",
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
        },
        series: [
            {
                name: "Écart positif",
                type: "bar",
                stack: "deviation",
                encode: { x: "date", y: "deviation_positive" },
                color: mapColors.value.hot,
                tooltip: { show: true },
            },
            {
                name: "Écart négatif",
                type: "bar",
                stack: "deviation",
                encode: { x: "date", y: "deviation_negative" },
                color: mapColors.value.cold,
                tooltip: { show: true },
            },
        ],
        title: {
            text: "France Métropolitaine",
            right: "right",
            top: -6,
        },
        axisPointer: {
            link: [{ xAxisIndex: "all" }],
            label: { backgroundColor: mapColors.value.chartAccentColor },
        },
        legend: { top: 230 },
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
        :loading-options="{ text: 'Chargement…', color: LOADING_SPIN_COLOR }"
        autoresize
        class="mt-5"
    />
</template>
