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
import { BarChart, ScatterChart } from "echarts/charts";
import { CanvasRenderer } from "echarts/renderers";
import { UniversalTransition } from "echarts/features";
import { recordsChartTooltipFormatter } from "~/components/charts/tooltipFormatters/recordsChartTooltipFormatter";
import {
    barSeries,
    buildTerritoryPlots,
    countByPeriod,
    scatterSeries,
} from "~/utils/recordsChartUtils";

echarts.registerLocale("FR", langFR);
echarts.use([
    GridComponent,
    TitleComponent,
    TooltipComponent,
    LegendComponent,
    DataZoomComponent,
    ScatterChart,
    BarChart,
    CanvasRenderer,
    UniversalTransition,
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

const option = computed<ECOption>(() => {
    const data = props.adapter.data.value;
    if (!data) return {};

    const selectedTerritories = props.adapter.selectedElements?.value ?? [];
    const selectedCount = selectedTerritories.length;
    const showStackedBar = selectedCount <= 1;

    const territoryPlots = buildTerritoryPlots(selectedTerritories, data);

    const plots = showStackedBar
        ? ["scatter", "bar"]
        : territoryPlots.map(() => "scatter");

    const barDataset = () => {
        const first = territoryPlots[0];
        if (!first) return [];
        const hotByPeriod = countByPeriod(
            first.hot,
            props.adapter.granularity.value,
        );
        const coldByPeriod = countByPeriod(
            first.cold,
            props.adapter.granularity.value,
        );
        return [
            {
                dimensions: ["period", "hot", "cold"],
                source: Object.keys({ ...hotByPeriod, ...coldByPeriod })
                    .sort()
                    .map((period) => ({
                        period,
                        hot: hotByPeriod[period] ?? 0,
                        cold: coldByPeriod[period] ?? 0,
                    })),
            },
        ];
    };

    return {
        dataset: [
            ...territoryPlots.flatMap((territory) => [
                {
                    dimensions: ["date", "value", "station"],
                    source: territory.hot,
                },
                {
                    dimensions: ["date", "value", "station"],
                    source: territory.cold,
                },
            ]),
            ...(showStackedBar ? barDataset() : []),
        ],
        grid: plots.map((_, index) => ({
            top: `${index * (100 / plots.length) + 8}%`,
            height: `${100 / plots.length - 15}%`,
            left: 30,
            right: 10,
        })),
        xAxis: plots.map((_, index) => ({
            type: "time",
            gridIndex: index,
            min: props.adapter.pickedDateStart?.value,
            max: props.adapter.pickedDateEnd?.value,
            nameLocation: "middle",
            nameGap: 25,
            nameTextStyle: { fontSize: 11, fontWeight: "bold" },
            axisPointer: { type: "line", label: { show: false } },
            boundaryGap: ["3%", "3%"],
            ...{
                year: {
                    axisLabel: { formatter: "{yyyy}" },
                },
                month: {
                    axisLabel: { formatter: "{MMM}-{yyyy}" },
                },
                day: {
                    axisLabel: { formatter: "{dd}-{MMM}-{yyyy}" },
                },
            }[props.adapter.granularity.value],
        })),
        yAxis: plots.map((plot, index) => ({
            type: "value",
            gridIndex: index,
            splitNumber: 3,
            name: plot === "bar" ? "Nombre de records" : "Température (°C)",
            nameRotate: 90,
            nameLocation: "middle",
            nameGap: 40,
            nameTextStyle: { fontSize: 10, fontWeight: "bold" },
            axisLabel: { fontSize: 10 },
            splitLine: { lineStyle: { type: "dashed" } },
        })),
        series: [
            ...territoryPlots.flatMap((_, index) => [
                scatterSeries({
                    name: "Records de chaleur",
                    datasetIndex: index * 2,
                    encode: { x: "date", y: "value" },
                    color: "#d32f2f",
                    symbolSize: 10,
                    xAxisIndex: index,
                    yAxisIndex: index,
                }),
                scatterSeries({
                    name: "Records de froid",
                    datasetIndex: index * 2 + 1,
                    encode: { x: "date", y: "value" },
                    color: "#1976d2",
                    symbolSize: 10,
                    xAxisIndex: index,
                    yAxisIndex: index,
                }),
            ]),
            ...(showStackedBar
                ? [
                      barSeries({
                          name: "Records de chaleur",
                          datasetIndex: territoryPlots.length * 2,
                          encode: { x: "period", y: "hot" },
                          color: "#d32f2f",
                          stack: "records",
                          xAxisIndex: 1,
                          yAxisIndex: 1,
                      }),
                      barSeries({
                          name: "Records de froid",
                          datasetIndex: territoryPlots.length * 2,
                          encode: { x: "period", y: "cold" },
                          color: "#1976d2",
                          stack: "records",
                          xAxisIndex: 1,
                          yAxisIndex: 1,
                      }),
                  ]
                : []),
        ],
        title: territoryPlots.map((plot, index) => ({
            text: plot.name,
            right: "right",
            top: `${index * (100 / plots.length) + 2}%`,
        })),
        axisPointer: {
            link: [{ xAxisIndex: "all" }],
            label: { backgroundColor: "#3a5080" },
        },
        legend: {
            data: ["Records de chaleur", "Records de froid"],
            bottom: -5,
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
                type: "inside",
                xAxisIndex: plots.map((_, i) => i),
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
