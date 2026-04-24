<script setup lang="ts">
import * as echarts from "echarts/core";
import langFR from "~/i18n/langFR.js";
import { useResizeObserver } from "@vueuse/core";
import type { SelectBarAdapter } from "~/components/ui/commons/selectBar/types";
import type { TemperatureRecordsGraphResponse } from "~/types/api";
import type { XAXisOption, YAXisOption } from "echarts/types/dist/shared";
import {
    barSeries,
    buildTerritoryPlots,
    countByPeriod,
    niceMax,
} from "~/utils/recordsChartUtils";
import { recordsPyramidTooltipFormatter } from "~/components/charts/tooltipFormatters/recordsPyramidTooltipFormatter";
import { COLORS } from "~/constants/colors";
type CategoryYAxisOption = Extract<YAXisOption, { type?: "category" }>;
type ValueXAxisOption = Extract<XAXisOption, { type?: "value" }>;

echarts.registerLocale("FR", langFR);

interface Props {
    adapter: SelectBarAdapter<TemperatureRecordsGraphResponse>;
}

const props = defineProps<Props>();

const containerRef = ref<HTMLElement | null>(null);
const INITIAL_CONTAINER_WIDTH = 900;
const containerWidth = ref(INITIAL_CONTAINER_WIDTH);
useResizeObserver(containerRef, (entries) => {
    const width = entries[0]?.contentRect.width;
    if (width !== undefined) containerWidth.value = width;
});

const renderer = ref<"svg" | "canvas">("canvas");
const initOptions = computed(() => ({
    height: 520,
    locale: "FR",
    renderer: renderer.value,
}));
provide(INIT_OPTIONS_KEY, initOptions);

function coldYAxis(opts: Partial<CategoryYAxisOption>): YAXisOption {
    return { type: "category", position: "right", ...opts };
}

function hotYAxis(opts: Partial<CategoryYAxisOption>): YAXisOption {
    return { type: "category", position: "left", ...opts };
}

function valueXAxis(opts: Partial<ValueXAxisOption>): XAXisOption {
    return { type: "value", ...opts };
}

const option = computed<ECOption>(() => {
    const data = props.adapter.data.value;
    if (!data) return {};

    const granularity = props.adapter.granularity.value;
    const selectedTerritories = props.adapter.selectedElements?.value ?? [];

    const territoryPlots = buildTerritoryPlots(selectedTerritories, data);

    const N = territoryPlots.length;

    // Agrégation par période pour chaque territoire
    const periodData = territoryPlots.map((plot) => {
        const hotByPeriod = countByPeriod(plot.hot, granularity);
        const coldByPeriod = countByPeriod(plot.cold, granularity);
        const allPeriods = Object.keys({
            ...hotByPeriod,
            ...coldByPeriod,
        }).sort();
        return { name: plot.name, hotByPeriod, coldByPeriod, allPeriods };
    });

    // Max global → échelle identique sur tous les sous-graphes
    const globalMax = niceMax(
        Math.max(
            ...periodData.flatMap(({ hotByPeriod, coldByPeriod }) => [
                ...Object.values(hotByPeriod),
                ...Object.values(coldByPeriod),
            ]),
            1,
        ),
    );

    const rightOfLeftGridPercent = { year: 53, month: 53.5, day: 54 }[
        granularity
    ];
    const rightOfLeftGrid = `${rightOfLeftGridPercent}%`;
    // margin calibré pour centrer le label à 50% quelle que soit la largeur du container
    const labelMargin = Math.round(
        ((rightOfLeftGridPercent - 50) / 100) * containerWidth.value,
    );
    const slotSize = 100 / N;

    // Positions verticales du subplot i dans le conteneur (en %)
    const gridTop = (i: number) => `${i * slotSize + 4}%`;
    const gridBottom = (i: number) =>
        i === N - 1 ? "12%" : `${(N - 1 - i) * slotSize + 4}%`;

    const xAxisBase: Partial<ValueXAxisOption> = {
        min: 0,
        max: globalMax,
        minInterval: 1,
        splitLine: { lineStyle: { type: "dashed" } },
    };

    const option: ECOption = {
        dataset: periodData.map(
            ({ hotByPeriod, coldByPeriod, allPeriods }) => ({
                dimensions: ["period", "hot", "cold"],
                source: allPeriods.map((period) => ({
                    period,
                    hot: hotByPeriod[period] ?? 0,
                    cold: coldByPeriod[period] ?? 0,
                })),
            }),
        ),
        grid: periodData.flatMap((_, i) => [
            {
                top: gridTop(i),
                bottom: gridBottom(i),
                left: "5%",
                right: rightOfLeftGrid,
            },
            {
                top: gridTop(i),
                bottom: gridBottom(i),
                left: rightOfLeftGrid,
                right: "5%",
            },
        ]),
        xAxis: periodData.flatMap((_, i) => [
            valueXAxis({ ...xAxisBase, gridIndex: 2 * i, inverse: true }),
            valueXAxis({ ...xAxisBase, gridIndex: 2 * i + 1 }),
        ]),
        axisPointer: { link: [{ yAxisIndex: "all" }] },
        yAxis: periodData.flatMap((pd, i) => [
            coldYAxis({
                data: pd.allPeriods,
                gridIndex: 2 * i,
                axisLabel: { show: false },
                axisLine: { show: true },
                axisPointer: { type: "shadow" },
            }),
            hotYAxis({
                data: pd.allPeriods,
                gridIndex: 2 * i + 1,
                axisLabel: {
                    margin: labelMargin,
                    width: labelMargin * 2,
                    align: "center",
                    fontSize: 12,
                    fontWeight: "bold",
                },
                axisTick: { show: false },
                axisLine: { lineStyle: { color: "#3a5080", width: 1 } },
                axisPointer: { type: "shadow" },
            }),
        ]),
        tooltip: {
            trigger: "axis",
            axisPointer: { type: "shadow" },
            formatter: recordsPyramidTooltipFormatter,
        },
        title: [
            ...periodData.map((pd, i) => ({
                text: pd.name,
                right: "right",
                top: `${i * slotSize + 2}%`,
                textStyle: { fontSize: 12 },
            })),
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
        series: periodData.flatMap((_, i) => [
            barSeries({
                name: "Records de froid",
                datasetIndex: i,
                encode: { x: "cold", y: "period" },
                color: COLORS.cold,
                xAxisIndex: 2 * i,
                yAxisIndex: 2 * i,
            }),
            barSeries({
                name: "Records de chaleur",
                datasetIndex: i,
                encode: { x: "hot", y: "period" },
                color: COLORS.hot,
                xAxisIndex: 2 * i + 1,
                yAxisIndex: 2 * i + 1,
            }),
        ]),
    };
    return option;
});
</script>

<template>
    <VChart
        :ref="adapter.chartRef"
        :key="`${adapter.granularity.value}-${adapter.chartType?.value}-${adapter.selectedElements?.value?.map((e) => e.id).join('-')}`"
        :option="option"
        :init-options="initOptions"
        :loading="adapter.pending.value"
        :loading-options="{ text: 'Chargement…', color: '#3b82f6' }"
        autoresize
    />
</template>
