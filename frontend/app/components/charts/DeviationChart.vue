<script setup lang="ts">
import * as echarts from "echarts/core";
import langFR from "~/i18n/langFR.js";
import type { SelectBarAdapter } from "../ui/commons/selectBar/types";
import type { DeviationResponse } from "~/types/api";
import { useDeviationStore } from "#imports";
import { deviationChartTooltipFormatter } from "./tooltipFormatters/deviationChartTooltipFormatter";
import {
    DataZoomComponent,
    GridComponent,
    LegendComponent,
    TitleComponent,
    TooltipComponent,
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
const { selectedStations, includeNational } = storeToRefs(useDeviationStore());
const props = defineProps<Props>();

const selectedStationsAndNationalNames = computed(() => {
    const stations = selectedStations.value.map(
        (station) => `${station.nom} (${station.departement})`,
    );
    return includeNational.value
        ? ["France Métropolitaine", ...stations]
        : stations;
});

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
    if (!data) {
        return {};
    }
    const stationsAndNational = includeNational.value
        ? [data.national, ...data.stations]
        : data.stations;
    const plotAmountToDisplay = stationsAndNational.length || 1;

    return {
        dataset:
            stationsAndNational.map((stationOrNational) => ({
                dimensions: [
                    "date",
                    "deviation_positive",
                    "deviation_negative",
                ],
                source:
                    stationOrNational?.data?.map((p) => ({
                        date: p.date,
                        deviation_positive:
                            p.deviation >= 0 ? p.deviation : null,
                        deviation_negative:
                            p.deviation < 0 ? p.deviation : null,
                    })) ?? [],
            })) ?? [],
        grid: stationsAndNational.map((_, index) => ({
            top: `${index * (100 / plotAmountToDisplay) + 3}%`,
            height: `${100 / plotAmountToDisplay - 10}%`,
            left: 30,
            right: 10,
            containLabel: true,
        })),
        xAxis: stationsAndNational.map((_, index) => ({
            type: "time",
            gridIndex: index,
            axisTick: { show: false },
            nameLocation: "middle",
            nameGap: 25,
            nameTextStyle: { fontSize: 11, fontWeight: "bold" },
            axisPointer: { type: "line", label: { show: false } },
        })),
        yAxis: stationsAndNational.map((_, index) => ({
            type: "value",
            gridIndex: index,
            splitNumber: 3,
            name: "Ecart à la normale (°C)",
            nameRotate: 90,
            nameLocation: "middle",
            nameGap: 40,
            nameTextStyle: { fontSize: 10, fontWeight: "bold" },
            axisLabel: { fontSize: 10 },
            splitLine: { lineStyle: { type: "dashed" } },
        })),
        series: stationsAndNational.flatMap((_, index) => [
            {
                name: "Ecart positif",
                type: "bar",
                stack: `deviation-${index}`,
                datasetIndex: index,
                encode: { x: "date", y: "deviation_positive" },
                color: "#d32f2f",
                tooltip: { show: true },
                xAxisIndex: index,
                yAxisIndex: index,
            },
            {
                name: "Ecart négatif",
                type: "bar",
                stack: `deviation-${index}`,
                datasetIndex: index,
                encode: { x: "date", y: "deviation_negative" },
                color: "#1976d2",
                tooltip: { show: true },
                xAxisIndex: index,
                yAxisIndex: index,
            },
        ]),
        title: stationsAndNational.map((stationOrNational, index) => ({
            text: selectedStationsAndNationalNames.value[index],
            right: "right",
            top: `${index * (100 / plotAmountToDisplay)}%`,
        })),
        axisPointer: {
            link: [{ xAxisIndex: "all" }],
            label: { backgroundColor: "#3a5080" },
        },
        legend: {
            bottom: 0,
        },
        tooltip: {
            trigger: "axis",
            axisPointer: { type: "line" },
            formatter: (params) =>
                deviationChartTooltipFormatter(
                    params,
                    props.adapter.granularity.value,
                    selectedStationsAndNationalNames.value,
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
</script>

<template>
    <div class="h-full">
        <div
            v-if="!props.adapter.data.value"
            class="flex flex-col justify-center h-full items-center text-stone-400"
        >
            <p>Selectionnez au moins une station</p>
            <p>
                pour afficher ces écarts à la normale, pour la période
                sélectionnée.
            </p>
        </div>
        <VChart
            v-else
            :ref="adapter.chartRef"
            :key="adapter.granularity.value"
            :option="option"
            :init-options="initOptions"
            :loading="adapter.pending.value"
            :loading-options="{ text: 'Chargement…', color: '#3b82f6' }"
            autoresize
        />
    </div>
</template>
