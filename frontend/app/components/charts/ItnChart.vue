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
                      : {
                            weekday: "short",
                            day: "numeric",
                            month: "short",
                            year: "numeric",
                        };
            const formattedDate = new Date(d.date as string).toLocaleDateString(
                "fr-FR",
                dateOptions,
            );

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
