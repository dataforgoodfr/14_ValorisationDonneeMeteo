<script setup lang="ts">
import * as echarts from "echarts/core";

import {
    TitleComponent,
    ToolboxComponent,
    TooltipComponent,
    GridComponent,
    DataZoomComponent,
    LegendComponent,
} from "echarts/components";
import { LineChart } from "echarts/charts";
import { UniversalTransition } from "echarts/features";
import { CanvasRenderer } from "echarts/renderers";

echarts.use([
    TitleComponent,
    ToolboxComponent,
    TooltipComponent,
    GridComponent,
    LineChart,
    CanvasRenderer,
    UniversalTransition,
    LegendComponent,
    DataZoomComponent,
]);

const itnStore = useItnStore();

// provide init-options
const renderer = ref<"svg" | "canvas">("svg");
const initOptions = computed(() => ({
    height: 600,
    renderer: renderer.value,
}));
provide(INIT_OPTIONS_KEY, initOptions);

const colorEcartType = "rgba(175, 175, 175, 1)";
const colorExtremes = "rgba(100, 100, 100, 0.2)";

const option = computed<ECOption>(() => ({
    dataset: {
        dimensions: [
            "date",
            "temperature",
            "baseline_mean",
            "baseline_std_dev_upper",
            "baseline_std_dev_lower",
            "baseline_std_dev_band",
            "baseline_max",
            "baseline_min",
            "baseline_band",
        ],
        source:
            itnStore.itnData?.time_series.map((point) => ({
                date: point.date,
                temperature: point.temperature,
                baseline_mean: point.baseline_mean,
                baseline_std_dev_upper: point.baseline_std_dev_upper,
                baseline_std_dev_lower: point.baseline_std_dev_lower,
                baseline_std_dev_band:
                    point.baseline_std_dev_upper - point.baseline_std_dev_lower,
                baseline_max: point.baseline_max,
                baseline_min: point.baseline_min,
                baseline_band: point.baseline_max - point.baseline_min,
            })) ?? [],
    },
    grid: {
        left: 10,
        right: 10,
        containLabel: true,
    },
    xAxis: { type: "time" },
    yAxis: {},
    series: [
        {
            // Invisible base — pushes the band up to start at lower bound
            type: "line",
            encode: { x: "date", y: "baseline_min" },
            stack: "extreme",
            symbol: "none",
            lineStyle: { opacity: 0 },
            areaStyle: { color: "transparent" },
            tooltip: { show: false },
        },
        {
            name: "Extrêmes",
            type: "line",
            encode: { x: "date", y: "baseline_band" },
            stack: "extreme",
            symbol: "none",
            color: colorExtremes,
            lineStyle: { opacity: 0 },
            areaStyle: { color: colorExtremes },
        },
        {
            // Invisible base — pushes the band up to start at lower bound
            type: "line",
            encode: { x: "date", y: "baseline_std_dev_lower" },
            stack: "std",
            symbol: "none",
            lineStyle: { opacity: 0 },
            areaStyle: { color: "transparent" },
            tooltip: { show: false },
        },
        {
            name: "Écart-type",
            type: "line",
            encode: { x: "date", y: "baseline_std_dev_band" },
            stack: "std",
            symbol: "none",
            color: colorEcartType,
            lineStyle: { opacity: 0 },
            areaStyle: { color: colorEcartType },
        },
        {
            name: "Indicateur MF",
            type: "line",
            encode: { x: "date", y: "temperature" },
            symbol: "none",
        },
    ],
    legend: {
        data: ["Indicateur MF", "Écart-type", "Extrêmes"],
        top: 0,
    },
    tooltip: {
        trigger: "axis",
        formatter: (params) => {
            if (!Array.isArray(params)) return "";
            const [first] = params;
            if (!first) return "";

            const d = first.value as Record<string, number | string>;
            const fmt = (v: number) => `${v.toFixed(2)}°C`;
            const find = (name: string) =>
                params.find((p) => p.seriesName === name);

            const dateOptions: Intl.DateTimeFormatOptions =
                itnStore.granularity === "month"
                    ? { year: "numeric", month: "long" }
                    : itnStore.granularity === "year"
                      ? { year: "numeric" }
                      : { weekday: "short", day: "numeric", month: "short", year: "numeric" };
            const formattedDate = new Date(d.date as string).toLocaleDateString("fr-FR", dateOptions);

            return [
                formattedDate,
                `${find("Extrêmes")?.marker ?? ""}Extrêmes : [${fmt(d.baseline_min as number)} – ${fmt(d.baseline_max as number)}]`,
                `${find("Écart-type")?.marker ?? ""}Écart-type : [${fmt(d.baseline_std_dev_lower as number)} – ${fmt(d.baseline_std_dev_upper as number)}]`,
                `${find("Indicateur MF")?.marker ?? ""}Indicateur MF : ${fmt(d.temperature as number)}`,
            ].join("<br/>");
        },
    },
    dataZoom: [
        {
            type: "slider",
            minSpan: 20,
        },
    ],
}));

const obj = [
    {
        componentType: "series",
        componentSubType: "line",
        componentIndex: 1,
        seriesType: "line",
        seriesIndex: 1,
        seriesId: "\u0000Extrêmes\u00000",
        seriesName: "Extrêmes",
        name: "",
        dataIndex: 8,
        data: {
            date: "2025-11-01",
            temperature: 8.02,
            baseline_mean: 7.87,
            baseline_std_dev_upper: 10.02,
            baseline_std_dev_lower: 5.71,
            baseline_std_dev_band: 4.31,
            baseline_max: 16.06,
            baseline_min: -0.34,
            baseline_band: 16.4,
        },
        value: {
            date: "2025-11-01",
            temperature: 8.02,
            baseline_mean: 7.87,
            baseline_std_dev_upper: 10.02,
            baseline_std_dev_lower: 5.71,
            baseline_std_dev_band: 4.31,
            baseline_max: 16.06,
            baseline_min: -0.34,
            baseline_band: 16.4,
        },
        color: "rgba(100, 100, 100, 0.2)",
        dimensionNames: [
            "date",
            "temperature",
            "baseline_mean",
            "baseline_std_dev_upper",
            "baseline_std_dev_lower",
            "baseline_std_dev_band",
            "baseline_max",
            "baseline_min",
            "baseline_band",
            null,
            null,
        ],
        encode: {
            x: [0],
            y: [8],
        },
        $vars: ["seriesName", "name", "value"],
        axisDim: "x",
        axisIndex: 0,
        axisType: "xAxis.time",
        axisId: "\u0000series\u00000\u00000",
        axisValue: 1761951600000,
        axisValueLabel: "2025-11-01",
        marker: '<span style="display:inline-block;margin-right:4px;border-radius:10px;width:10px;height:10px;background-color:rgba(100, 100, 100, 0.2);"></span>',
    },
    {
        componentType: "series",
        componentSubType: "line",
        componentIndex: 3,
        seriesType: "line",
        seriesIndex: 3,
        seriesId: "\u0000Écart-type\u00000",
        seriesName: "Écart-type",
        name: "",
        dataIndex: 8,
        data: {
            date: "2025-11-01",
            temperature: 8.02,
            baseline_mean: 7.87,
            baseline_std_dev_upper: 10.02,
            baseline_std_dev_lower: 5.71,
            baseline_std_dev_band: 4.31,
            baseline_max: 16.06,
            baseline_min: -0.34,
            baseline_band: 16.4,
        },
        value: {
            date: "2025-11-01",
            temperature: 8.02,
            baseline_mean: 7.87,
            baseline_std_dev_upper: 10.02,
            baseline_std_dev_lower: 5.71,
            baseline_std_dev_band: 4.31,
            baseline_max: 16.06,
            baseline_min: -0.34,
            baseline_band: 16.4,
        },
        color: "rgba(175, 175, 175, 1)",
        dimensionNames: [
            "date",
            "temperature",
            "baseline_mean",
            "baseline_std_dev_upper",
            "baseline_std_dev_lower",
            "baseline_std_dev_band",
            "baseline_max",
            "baseline_min",
            "baseline_band",
            null,
            null,
        ],
        encode: {
            x: [0],
            y: [5],
        },
        $vars: ["seriesName", "name", "value"],
        axisDim: "x",
        axisIndex: 0,
        axisType: "xAxis.time",
        axisId: "\u0000series\u00000\u00000",
        axisValue: 1761951600000,
        axisValueLabel: "2025-11-01",
        marker: '<span style="display:inline-block;margin-right:4px;border-radius:10px;width:10px;height:10px;background-color:rgba(175, 175, 175, 1);"></span>',
    },
    {
        componentType: "series",
        componentSubType: "line",
        componentIndex: 4,
        seriesType: "line",
        seriesIndex: 4,
        seriesId: "\u0000Indicateur MF\u00000",
        seriesName: "Indicateur MF",
        name: "",
        dataIndex: 8,
        data: {
            date: "2025-11-01",
            temperature: 8.02,
            baseline_mean: 7.87,
            baseline_std_dev_upper: 10.02,
            baseline_std_dev_lower: 5.71,
            baseline_std_dev_band: 4.31,
            baseline_max: 16.06,
            baseline_min: -0.34,
            baseline_band: 16.4,
        },
        value: {
            date: "2025-11-01",
            temperature: 8.02,
            baseline_mean: 7.87,
            baseline_std_dev_upper: 10.02,
            baseline_std_dev_lower: 5.71,
            baseline_std_dev_band: 4.31,
            baseline_max: 16.06,
            baseline_min: -0.34,
            baseline_band: 16.4,
        },
        color: "#505372",
        dimensionNames: [
            "date",
            "temperature",
            "baseline_mean",
            "baseline_std_dev_upper",
            "baseline_std_dev_lower",
            "baseline_std_dev_band",
            "baseline_max",
            "baseline_min",
            "baseline_band",
        ],
        encode: {
            x: [0],
            y: [1],
        },
        $vars: ["seriesName", "name", "value"],
        axisDim: "x",
        axisIndex: 0,
        axisType: "xAxis.time",
        axisId: "\u0000series\u00000\u00000",
        axisValue: 1761951600000,
        axisValueLabel: "2025-11-01",
        marker: '<span style="display:inline-block;margin-right:4px;border-radius:10px;width:10px;height:10px;background-color:#505372;"></span>',
    },
];
</script>

<template>
    <VChart
        :option="option"
        :init-options="initOptions"
        :loading="itnStore.pending"
        :loading-options="{ text: 'Chargement…', color: '#3b82f6' }"
        autoresize
    />
</template>
