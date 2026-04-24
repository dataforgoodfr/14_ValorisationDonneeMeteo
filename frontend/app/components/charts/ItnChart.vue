<script setup lang="ts">
import * as echarts from "echarts/core";
import langFR from "~/i18n/langFR.js";
import type { SelectBarAdapter } from "~/components/ui/commons/selectBar/types";
import type {
    NationalIndicatorDataPoint,
    NationalIndicatorResponse,
} from "~/types/api";
import { CHART_ATTRIBUTION_GRAPHIC } from "~/constants/chartAttribution";
import { ITN_SERIES, ITN_COLORS } from "~/constants/itn";
import { itnChartTooltipFormatter } from "./tooltipFormatters/itnChartTooltipFormatter";
import {
    itnStackedTooltipFormatter,
    formatStackedAxisLabel,
    formatContinuousAxisLabel,
} from "./tooltipFormatters/itnStackedTooltipFormatter";
import {
    DataZoomComponent,
    GraphicComponent,
    GridComponent,
    LegendComponent,
    TitleComponent,
    ToolboxComponent,
    TooltipComponent,
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
    GraphicComponent,
]);

interface Props {
    adapter: SelectBarAdapter<NationalIndicatorResponse>;
}

const props = defineProps<Props>();

// provide init-options
const renderer = ref<"svg" | "canvas">("canvas");
const initOptions = computed(() => ({
    height: 600,
    locale: "FR",
    renderer: renderer.value,
}));
provide(INIT_OPTIONS_KEY, initOptions);

const colorEcartType = ITN_COLORS.ECART_TYPE;
const colorExtremes = ITN_COLORS.EXTREMES;

function buildStackedOption(
    timeSeries: NationalIndicatorDataPoint[],
    granularity: "month" | "day",
): ECOption {
    function getXKey(dateStr: string): string {
        const d = new Date(dateStr);
        const m = String(d.getMonth() + 1).padStart(2, "0");
        return granularity === "month"
            ? m
            : `${m}-${String(d.getDate()).padStart(2, "0")}`;
    }

    const allPositions = [
        ...new Set(timeSeries.map((p) => getXKey(p.date))),
    ].sort();

    // Baseline: première occurrence par position (identique pour toutes les années)
    const baselineByPos = new Map<string, NationalIndicatorDataPoint>();
    for (const p of timeSeries) {
        const k = getXKey(p.date);
        if (!baselineByPos.has(k)) baselineByPos.set(k, p);
    }

    // Températures par année
    const byYear = new Map<number, Map<string, number>>();
    for (const p of timeSeries) {
        const year = new Date(p.date).getFullYear();
        const k = getXKey(p.date);
        if (!byYear.has(year)) byYear.set(year, new Map());
        byYear.get(year)!.set(k, p.temperature);
    }
    const years = [...byYear.keys()].sort();

    const baselineSource = allPositions.map((pos) => {
        const p = baselineByPos.get(pos)!;
        return [
            pos,
            p.baseline_min,
            p.baseline_max - p.baseline_min,
            p.baseline_std_dev_lower,
            p.baseline_std_dev_upper - p.baseline_std_dev_lower,
            p.baseline_mean,
        ];
    });

    const baselineSeries: ECOption["series"] = [
        {
            type: "line",
            encode: { x: "position", y: "baseline_min" },
            stack: "extreme",
            stackStrategy: "all",
            symbol: "none",
            lineStyle: { opacity: 0 },
            areaStyle: { color: "transparent" },
            tooltip: { show: false },
        },
        {
            name: ITN_SERIES.extremes,
            type: "line",
            encode: { x: "position", y: "baseline_band" },
            stack: "extreme",
            stackStrategy: "all",
            symbol: "none",
            color: colorExtremes,
            lineStyle: { opacity: 0 },
            areaStyle: { color: colorExtremes },
        },
        {
            type: "line",
            encode: { x: "position", y: "baseline_std_dev_lower" },
            stack: "std",
            stackStrategy: "all",
            symbol: "none",
            lineStyle: { opacity: 0 },
            areaStyle: { color: "transparent" },
            tooltip: { show: false },
        },
        {
            name: ITN_SERIES.stdDev,
            type: "line",
            encode: { x: "position", y: "baseline_std_dev_band" },
            stack: "std",
            stackStrategy: "all",
            symbol: "none",
            color: colorEcartType,
            lineStyle: { opacity: 0 },
            areaStyle: { color: colorEcartType },
        },
        {
            name: ITN_SERIES.temperature,
            type: "line",
            encode: { x: "position", y: "baseline_mean" },
            symbol: "none",
            lineStyle: { width: 2, color: "#333" },
            z: 5,
        },
    ];

    const yearSeries: ECOption["series"] = years.map((year) => ({
        name: String(year),
        type: "line",
        data: allPositions.map((pos) => [
            pos,
            byYear.get(year)?.get(pos) ?? null,
        ]),
        symbol: "none",
        lineStyle: { width: 1.5 },
        connectNulls: false,
        z: 10,
    }));

    return {
        dataset: {
            dimensions: [
                "position",
                "baseline_min",
                "baseline_band",
                "baseline_std_dev_lower",
                "baseline_std_dev_band",
                "baseline_mean",
            ],
            source: baselineSource,
        },
        grid: { left: 30, right: 10, bottom: 150, containLabel: true },
        xAxis: {
            type: "category",
            data: allPositions,
            axisLabel: {
                interval:
                    granularity === "day"
                        ? (_index: number, value: string) =>
                              value.endsWith("-01")
                        : 0,
                formatter: (val: string) =>
                    formatStackedAxisLabel(val, granularity),
            },
        },
        yAxis: {
            type: "value",
            name: "Température (°C)",
            nameRotate: 90,
            nameLocation: "middle",
            nameGap: 40,
        },
        series: [...baselineSeries, ...yearSeries],
        legend: {
            data: [
                ITN_SERIES.extremes,
                ITN_SERIES.baseline,
                ITN_SERIES.temperature,
                ...years.map(String),
            ],
            bottom: 85,
        },
        title: { text: "Indicateur thermique national", left: "center" },
        tooltip: {
            trigger: "axis",
            formatter: (params) =>
                itnStackedTooltipFormatter(params, granularity),
        },
        emphasis: { focus: "none", disabled: true },
        graphic: CHART_ATTRIBUTION_GRAPHIC,
    };
}

const option = computed<ECOption>(() => {
    const data = props.adapter.data.value;

    if (props.adapter.chartType?.value === "stacked" && data) {
        const gran = props.adapter.granularity.value;
        return buildStackedOption(
            data.time_series,
            gran === "year" ? "month" : gran,
        );
    }

    const timeSeries = insertCrossingPoints(data?.time_series ?? []);

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
            left: 30,
            right: 10,
            bottom: 150,
            containLabel: true,
        },
        xAxis: {
            type: "time",
            ...(props.adapter.granularity.value === "day"
                ? {
                      axisLabel: {
                          formatter: formatContinuousAxisLabel,
                      },
                  }
                : {}),
        },
        yAxis: {
            type: "value",
            name: "Température (°C)",
            nameRotate: 90,
            nameLocation: "middle",
            nameGap: 40,
        },
        series: [
            // extreme - Invisible base — pushes the band up to start at lower bound
            {
                type: "line",
                encode: { x: "date", y: "baseline_min" },
                stack: "extreme",
                stackStrategy: "all",
                symbol: "none",
                lineStyle: { opacity: 0 },
                areaStyle: { color: "transparent" },
                tooltip: { show: false },
            },
            // extreme - baseline_band
            {
                name: ITN_SERIES.extremes,
                type: "line",
                encode: { x: "date", y: "baseline_band" },
                stack: "extreme",
                stackStrategy: "all",
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
                stackStrategy: "all",
                symbol: "none",
                lineStyle: { opacity: 0 },
                areaStyle: { color: "transparent" },
                tooltip: { show: false },
            },
            // ecart-type - baseline_std_dev_band
            {
                name: ITN_SERIES.stdDev,
                type: "line",
                encode: { x: "date", y: "baseline_std_dev_band" },
                stack: "std",
                stackStrategy: "all",
                symbol: "none",
                color: colorEcartType,
                lineStyle: { opacity: 0 },
                areaStyle: { color: colorEcartType },
            },
            // Moyenne - baseline_mean
            {
                name: ITN_SERIES.baseline,
                type: "line",
                encode: { x: "date", y: "baseline_mean" },
                symbol: "none",
            },
            // Temperature - temperature
            {
                name: ITN_SERIES.temperature,
                type: "line",
                stack: "temperature",
                encode: { x: "date", y: "temperature" },
                color: "#999",
                lineStyle: { width: 0.5 },
                symbol: "none",
            },
            // hot_cold_invisible_band
            {
                name: ITN_SERIES.temperature,
                type: "line",
                encode: { x: "date", y: "hot_cold_invisible_band" },
                stack: "hot_cold",
                stackStrategy: "all",
                symbol: "none",
                lineStyle: { opacity: 0 },
                areaStyle: { color: "transparent" },
                tooltip: { show: false },
            },
            // hot_red_band
            {
                name: ITN_SERIES.temperature,
                type: "line",
                encode: { x: "date", y: "hot_red_band" },
                stack: "hot_cold",
                stackStrategy: "all",
                symbol: "none",
                color: "#f00",
                lineStyle: { opacity: 0 },
                areaStyle: { color: "rgba(255, 0, 0, 0.6)" },
                tooltip: { show: false },
            },
            // cold_blue_band
            {
                name: ITN_SERIES.temperature,
                type: "line",
                encode: { x: "date", y: "cold_blue_band" },
                stack: "hot_cold",
                stackStrategy: "all",
                symbol: "none",
                color: "#00f",
                lineStyle: { opacity: 0 },
                areaStyle: { color: "rgba(0, 0, 255, 0.6)" },
                tooltip: { show: false },
            },
        ],
        title: {
            text: "Indicateur thermique national",
            left: "center",
        },
        legend: {
            data: [
                ITN_SERIES.temperature,
                ITN_SERIES.baseline,
                ITN_SERIES.stdDev,
                ITN_SERIES.extremes,
            ],
            bottom: 85,
        },
        tooltip: {
            trigger: "axis",
            formatter: (params) =>
                itnChartTooltipFormatter(
                    params,
                    props.adapter.granularity.value,
                ),
        },
        dataZoom: [{ type: "inside", minSpan: 20 }],
        emphasis: {
            focus: "none",
            disabled: true, // disables all emphasis state changes on hover
        },
        graphic: CHART_ATTRIBUTION_GRAPHIC,
    };
});
</script>

<template>
    <VChart
        :ref="adapter.chartRef"
        :key="`${adapter.granularity.value}-${adapter.chartType?.value ?? 'line'}`"
        :option="option"
        :init-options="initOptions"
        :loading="adapter.pending.value"
        :loading-options="{ text: 'Chargement…', color: '#3b82f6' }"
        autoresize
    />
</template>
