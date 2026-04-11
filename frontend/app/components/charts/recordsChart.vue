<script setup lang="ts">
import * as echarts from "echarts/core";
import langFR from "~/i18n/langFR.js";
import type { SelectBarAdapter } from "~/components/ui/commons/selectBar/types";
import type { TemperatureRecordsResponse } from "~/types/api";
import {
    DataZoomComponent,
    GridComponent,
    LegendComponent,
    TitleComponent,
    TooltipComponent,
} from "echarts/components";
import { ScatterChart, BarChart } from "echarts/charts";
import { UniversalTransition } from "echarts/features";
import { CanvasRenderer } from "echarts/renderers";
import { recordsChartTooltipFormatter } from "./tooltipFormatters/recordsChartTooltipFormatter";

echarts.registerLocale("FR", langFR);
echarts.use([
    TitleComponent,
    TooltipComponent,
    GridComponent,
    ScatterChart,
    BarChart,
    LegendComponent,
    DataZoomComponent,
    UniversalTransition,
    CanvasRenderer,
]);

interface Props {
    adapter: SelectBarAdapter<TemperatureRecordsResponse>;
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

// ── Option scatter (ton code existant, inchangé) ─────────────────────────────
const scatterOption = computed<ECOption>(() => {
    const data = props.adapter.data.value;
    if (!data) return {};

    const hotRecords = data.stations.flatMap((station) =>
        station.hot_records.map((record) => ({
            date: record.date,
            value: record.value,
            station: station.name,
        })),
    );

    const coldRecords = data.stations.flatMap((station) =>
        station.cold_records.map((record) => ({
            date: record.date,
            value: record.value,
            station: station.name,
        })),
    );

    return {
        dataset: [
            {
                dimensions: ["date", "value", "station"],
                source: hotRecords,
            },
            {
                dimensions: ["date", "value", "station"],
                source: coldRecords,
            },
        ],
        grid: { left: 30, right: 10, containLabel: true },
        xAxis: {
            type: "time",
            min: props.adapter.pickedDateStart?.value,
            max: props.adapter.pickedDateEnd?.value,
            nameLocation: "middle",
            nameGap: 25,
            nameTextStyle: { fontSize: 11, fontWeight: "bold" },
            axisPointer: { type: "line", label: { show: false } },
        },
        yAxis: {
            type: "value",
            splitNumber: 3,
            name: "Température (°C)",
            nameRotate: 90,
            nameLocation: "middle",
            nameGap: 40,
            nameTextStyle: { fontSize: 10, fontWeight: "bold" },
            axisLabel: { fontSize: 10 },
            splitLine: { lineStyle: { type: "dashed" } },
        },
        series: [
            {
                name: "Records de chaleur",
                type: "scatter",
                datasetIndex: 0,
                encode: {
                    x: "date",
                    y: "value",
                },
                color: "#d32f2f",
                symbolSize: 10,
                tooltip: { show: true },
            },
            {
                name: "Records de froid",
                type: "scatter",
                datasetIndex: 1,
                encode: {
                    x: "date",
                    y: "value",
                },
                color: "#1976d2",
                symbolSize: 10,
                tooltip: { show: true },
            },
        ],
        title: {
            text: "France Métropolitaine",
            right: "right",
            top: 10,
        },
        axisPointer: {
            link: [{ xAxisIndex: "all" }],
            label: { backgroundColor: "#3a5080" },
        },
        legend: {
            data: ["Records de chaleur", "Records de froid"],
            bottom: 0,
        },
        tooltip: {
            trigger: "item",
            axisPointer: { type: "cross" },
            formatter: (params) =>
                recordsChartTooltipFormatter(
                    params,
                    props.adapter.granularity.value,
                ),
        },
        dataZoom: [
            {
                xAxisIndex: "all",
                type: "inside",
                minSpan: 20,
            },
        ],
    };
});

// ── Option pyramide ──────────────────────────────────────────────────────────
const pyramidOption = computed<ECOption>(() => {
    const data = props.adapter.data.value;
    if (!data) return {};
    return useRecordsPyramidOption(
        data,
        props.adapter.granularity.value,
    ) as ECOption;
});

// ── Switch final ─────────────────────────────────────────────────────────────
const option = computed<ECOption>(() =>
    props.adapter.chartType?.value === "pyramid"
        ? pyramidOption.value
        : scatterOption.value,
);
</script>

<template>
    <VChart
        :ref="adapter.chartRef"
        :key="`${adapter.granularity.value}-${adapter.chartType?.value}`"
        :option="option"
        :init-options="initOptions"
        :loading="adapter.pending.value"
        :loading-options="{ text: 'Chargement…', color: '#3b82f6' }"
        autoresize
    />
</template>
