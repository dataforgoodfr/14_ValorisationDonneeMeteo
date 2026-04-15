<script setup lang="ts">
import * as echarts from "echarts/core";
import langFR from "~/i18n/langFR.js";
import type { SelectBarAdapter } from "~/components/ui/commons/selectBar/types";
import type { TemperatureRecordsResponse } from "~/types/api";
import {
    countByPeriod,
    flattenColdRecords,
    flattenHotRecords,
    niceMax,
} from "./recordsChartUtils";
import { recordsPyramidTooltipFormatter } from "../tooltipFormatters/recordsPyramidTooltipFormatter";

echarts.registerLocale("FR", langFR);

interface Props {
    adapter: SelectBarAdapter<TemperatureRecordsResponse>;
}

const props = defineProps<Props>();

const renderer = ref<"svg" | "canvas">("canvas");
const initOptions = computed(() => ({
    height: 600,
    locale: "FR",
    renderer: renderer.value,
}));
provide(INIT_OPTIONS_KEY, initOptions);

const option = computed<ECOption>(() => {
    const data = props.adapter.data.value;
    if (!data) return {};

    const hotRecords = flattenHotRecords(data);
    const coldRecords = flattenColdRecords(data);
    const hotByPeriod = countByPeriod(
        hotRecords,
        props.adapter.granularity.value,
    );
    const coldByPeriod = countByPeriod(
        coldRecords,
        props.adapter.granularity.value,
    );
    const rightOfLeftGrid = { year: "53%", month: "53.5%", day: "54%" }[
        props.adapter.granularity.value
    ];
    const labelMargin = { year: 27, month: 31, day: 35 }[
        props.adapter.granularity.value
    ];

    const maxCount = Math.max(
        ...Object.values(hotByPeriod),
        ...Object.values(coldByPeriod),
        1,
    );

    const xAxisBase = {
        type: "value" as const,
        min: 0,
        max: niceMax(maxCount),
        minInterval: 1,
        splitLine: { lineStyle: { type: "dashed" as const } },
    };

    return {
        dataset: {
            dimensions: ["period", "hot", "cold"],
            source: Object.keys({ ...hotByPeriod, ...coldByPeriod })
                .sort()
                .map((period) => ({
                    period,
                    hot: hotByPeriod[period] ?? 0,
                    cold: coldByPeriod[period] ?? 0,
                })),
        },
        grid: [
            { top: "8%", bottom: "12%", left: "5%", right: rightOfLeftGrid },
            { top: "8%", bottom: "12%", left: rightOfLeftGrid, right: "5%" },
        ],
        xAxis: [
            { ...xAxisBase, gridIndex: 0, inverse: true },
            { ...xAxisBase, gridIndex: 1 },
        ],
        axisPointer: {
            link: [{ yAxisIndex: "all" }],
        },
        yAxis: [
            {
                type: "category",
                gridIndex: 0,
                position: "right",
                axisLabel: { show: false },
                axisLine: { show: true },
                axisPointer: { type: "shadow" },
            }, // gauche, labels cachés
            {
                type: "category",
                gridIndex: 1,
                position: "left",
                axisLabel: {
                    margin: labelMargin,
                    align: "center",
                    fontSize: 12,
                    fontWeight: "bold",
                },
                axisTick: { show: false },
                axisLine: { lineStyle: { color: "#3a5080", width: 1 } },
                axisPointer: { type: "shadow" },
            }, // droite, labels visibles au centre
        ],
        tooltip: {
            trigger: "axis",
            axisPointer: { type: "shadow" },
            formatter: recordsPyramidTooltipFormatter,
        },
        title: [
            {
                text: "France Métropolitaine",
                right: "right",
                top: 10,
            },
            {
                text: "Nombre de records",
                bottom: 25,
                left: "50%",
                textAlign: "center",
                textStyle: { fontSize: 12, color: "#000000" },
            },
        ],
        legend: {
            data: ["Records de froid", "Records de chaleur"],
            bottom: 0,
        },
        series: [
            {
                name: "Records de froid",
                type: "bar",
                encode: { x: "cold", y: "period" },
                color: "#1976d2",
                xAxisIndex: 0,
                yAxisIndex: 0,
            },
            {
                name: "Records de chaleur",
                type: "bar",
                encode: { x: "hot", y: "period" },
                color: "#d32f2f",
                xAxisIndex: 1,
                yAxisIndex: 1,
            },
        ],
    };
});
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
