<script setup lang="ts">
import * as echarts from "echarts/core";
import langFR from "~/i18n/langFR.js";

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
echarts.registerLocale("FR", langFR);
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
    locale: "FR",
    renderer: renderer.value,
}));
provide(INIT_OPTIONS_KEY, initOptions);

const colorEcartType = "rgba(175, 175, 175, 1)";
const colorExtremes = "rgba(100, 100, 100, 0.2)";

const option = computed<ECOption>(() => {
    const timeSeries = insertCrossingPoints(
        itnStore.itnData?.time_series ?? [],
    );

    return {
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
                "hot_red_band",
                "cold_blue_band",
                "hot_cold_invisible_band",
                "isInterpolated",
            ],
            source:
                timeSeries.map((point) => ({
                    date: point.date,
                    temperature: point.temperature,
                    baseline_mean: point.baseline_mean,
                    baseline_std_dev_upper: point.baseline_std_dev_upper,
                    baseline_std_dev_lower: point.baseline_std_dev_lower,
                    baseline_std_dev_band:
                        point.baseline_std_dev_upper -
                        point.baseline_std_dev_lower,
                    baseline_max: point.baseline_max,
                    baseline_min: point.baseline_min,
                    baseline_band: point.baseline_max - point.baseline_min,
                    cold_blue_band:
                        point.baseline_mean -
                        Math.min(point.temperature, point.baseline_mean),
                    hot_red_band:
                        point.temperature -
                        Math.min(point.temperature, point.baseline_mean),
                    hot_cold_invisible_band: Math.min(
                        point.temperature,
                        point.baseline_mean,
                    ),
                    isInterpolated: point.isInterpolated ? 1 : 0,
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
            // extreme - Invisible base — pushes the band up to start at lower bound
            {
                type: "line",
                encode: { x: "date", y: "baseline_min" },
                stack: "extreme",
                symbol: "none",
                lineStyle: { opacity: 0 },
                areaStyle: { color: "transparent" },
                tooltip: { show: false },
            },
            // extreme - baseline_band
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
            // ecart-type - Invisible base — pushes the band up to start at lower bound
            {
                type: "line",
                encode: { x: "date", y: "baseline_std_dev_lower" },
                stack: "std",
                symbol: "none",
                lineStyle: { opacity: 0 },
                areaStyle: { color: "transparent" },
                tooltip: { show: false },
            },
            // ecart-type - baseline_std_dev_band
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
            // Moyenne - baseline_mean
            {
                name: "Indicateur MF",
                type: "line",
                encode: { x: "date", y: "baseline_mean" },
                symbol: "none",
            },
            // Temperature - temperature
            {
                name: "Température",
                type: "line",
                stack: "temperature",
                encode: { x: "date", y: "temperature" },
                color: "#999",
                lineStyle: { width: 0.5 },
                symbol: "none",
            },
            // hot_cold_invisible_band
            {
                name: "Température",
                type: "line",
                encode: { x: "date", y: "hot_cold_invisible_band" },
                stack: "hot_cold",
                symbol: "none",
                lineStyle: { opacity: 0 },
                areaStyle: { color: "transparent" },
                tooltip: { show: false },
            },
            // hot_red_band
            {
                name: "Température",
                type: "line",
                encode: { x: "date", y: "hot_red_band" },
                stack: "hot_cold",
                symbol: "none",
                color: "#f00",
                lineStyle: { opacity: 0 },
                areaStyle: { color: "rgba(255, 0, 0, 0.6)" },
                tooltip: { show: false },
            },
            // cold_blue_band
            {
                name: "Température",
                type: "line",
                encode: { x: "date", y: "cold_blue_band" },
                stack: "hot_cold",
                symbol: "none",
                color: "#00f",
                lineStyle: { opacity: 0 },
                areaStyle: { color: "rgba(0, 0, 255, 0.6)" },
                tooltip: { show: false },
            },
        ],
        legend: {
            data: ["Température", "Indicateur MF", "Écart-type", "Extrêmes"],
            top: 0,
        },
        tooltip: {
            trigger: "axis",
            formatter: (params) => {
                if (!Array.isArray(params)) return "";
                const [first] = params;
                if (!first) return "";

                const d = first.value as Record<string, number | string>;
                if (d.isInterpolated) return "";
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
                const formattedDate = new Date(
                    d.date as string,
                ).toLocaleDateString("fr-FR", dateOptions);

                return [
                    formattedDate,
                    `${find("Température")?.marker ?? ""}Température : ${fmt(d.temperature as number)}`,
                    `${find("Indicateur MF")?.marker ?? ""}Indicateur MF : ${fmt(d.baseline_mean as number)}`,
                    `${find("Extrêmes")?.marker ?? ""}Extrêmes : [${fmt(d.baseline_min as number)} – ${fmt(d.baseline_max as number)}]`,
                    `${find("Écart-type")?.marker ?? ""}Écart-type : [${fmt(d.baseline_std_dev_lower as number)} – ${fmt(d.baseline_std_dev_upper as number)}]`,
                ].join("<br/>");
            },
        },
        dataZoom: [
            {
                type: "slider",
                minSpan: 20,
            },
        ],
    };
});
</script>

<template>
    <VChart
        :key="itnStore.granularity"
        :option="option"
        :init-options="initOptions"
        :loading="itnStore.pending"
        :loading-options="{ text: 'Chargement…', color: '#3b82f6' }"
        autoresize
    />
</template>
