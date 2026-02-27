<script setup lang="ts">
import * as echarts from "echarts/core";

import {
    TitleComponent,
    ToolboxComponent,
    TooltipComponent,
    GridComponent,
    DataZoomComponent,
} from "echarts/components";
import { LineChart } from "echarts/charts";
import { UniversalTransition } from "echarts/features";
import { CanvasRenderer } from "echarts/renderers";

echarts.use([
    TitleComponent,
    ToolboxComponent,
    TooltipComponent,
    GridComponent,
    DataZoomComponent,
    LineChart,
    CanvasRenderer,
    UniversalTransition,
]);

const itnStore = useItnStore();

// provide init-options
const renderer = ref<"svg" | "canvas">("svg");
const initOptions = computed(() => ({
    width: "auto",
    height: 600,
    renderer: renderer.value,
}));
provide(INIT_OPTIONS_KEY, initOptions);

const option = computed<ECOption>(() => ({
    dataset: {
        dimensions: [
            "date",
            "temperature",
            "baseline_mean",
            "baseline_std_dev_upper",
            "baseline_std_dev_lower",
            "baseline_max",
            "baseline_min",
        ],
        source: itnStore.itnData?.time_series.map((point) => ({
            date: point.date,
            temperature: point.temperature,
            baseline_mean: point.baseline_mean,
            baseline_std_dev_upper: point.baseline_std_dev_upper,
            baseline_std_dev_lower: point.baseline_std_dev_lower,
            baseline_max: point.baseline_max,
            baseline_min: point.baseline_min,
        })),
    },
    grid: {
        left: 10,
        right: 10,
        containLabel: true,
    },
    xAxis: {
        type: "time",
    },
    yAxis: {},
    series: [{ type: "line" }],
}));
</script>

<template>
    <VChart :option="option" :init-options="initOptions" autoresize />
</template>
