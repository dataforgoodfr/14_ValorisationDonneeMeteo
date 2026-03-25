<script setup lang="ts">
import * as echarts from "echarts/core";
import langFR from "~/i18n/langFR.js";
import type { SelectBarAdapter } from "../ui/commons/selectBar/types";
import type { DeviationResponse } from "~/types/api";
import { deviationChartTooltipFormatter } from "./tooltipFormatters/deviationChartTooltipFormatter";
import {
    TitleComponent,
    TooltipComponent,
    GridComponent,
    DataZoomComponent,
    LegendComponent,
} from "echarts/components";
import { BarChart } from "echarts/charts";
import { UniversalTransition } from "echarts/features";
import { CanvasRenderer } from "echarts/renderers";
echarts.registerLocale("FR", langFR);
echarts.use([
    TitleComponent,
    TooltipComponent,
    GridComponent,
    BarChart,
    LegendComponent,
    DataZoomComponent,
    UniversalTransition,
    CanvasRenderer,
]);

interface Props {
    adapter: SelectBarAdapter<DeviationResponse>;
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

const option = computed<ECOption>(() => {
    const data = props.adapter.data.value?.national.data;

    return {
        dataset: {
            dimensions: [
                "date",
                "deviation",
                "deviation_positive",
                "deviation_negative",
            ],
            source:
                data?.map((p) => ({
                    date: p.date,
                    deviation: p.deviation,
                    deviation_positive: p.deviation >= 0 ? p.deviation : null,
                    deviation_negative: p.deviation < 0 ? p.deviation : null,
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
            axisTick: { show: false },
            nameLocation: "middle",
            nameGap: 25,
            nameTextStyle: { fontSize: 11, fontWeight: "bold" },
            axisPointer: { type: "shadow", label: { show: false } },
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
                name: "Ecart positif",
                type: "bar",
                stack: "deviation",
                encode: { x: "date", y: "deviation_positive" },
                color: "#d32f2f",
                tooltip: { show: true },
            },
            {
                name: "Ecart négatif",
                type: "bar",
                stack: "deviation",
                encode: { x: "date", y: "deviation_negative" },
                color: "#1976d2",
                tooltip: { show: true },
            },
        ],
        title: {
            text: "Ecart à la normale",
            left: "center",
        },
        legend: {
            data: ["Ecart positif", "Ecart négatif"],
            bottom: 85,
        },
        tooltip: {
            trigger: "axis",
            axisPointer: { type: "shadow" },
            formatter: (params) =>
                deviationChartTooltipFormatter(
                    params,
                    props.adapter.granularity.value,
                ),
        },
        dataZoom: [
            {
                type: "slider",
                minSpan: 20,
                showDataShadow: false,
            },
            {
                type: "inside",
                minSpan: 20,
            },
        ],
    };
});
</script>

<template>
    <VChart
        :ref="adapter.chartRef"
        :key="adapter.granularity.value"
        :option="option"
        :init-options="initOptions"
        :loading="adapter.pending.value"
        :loading-options="{ text: 'Chargement…', color: '#3b82f6' }"
        autoresize
    />
</template>
