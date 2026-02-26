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

const data = {
    metadata: {
        date_start: "2024-01-01",
        date_end: "2025-01-01",
        baseline: "1991-2020",
        granularity: "month",
        slice_type: "full",
    },
    time_series: [
        {
            date: "2024-01-01",
            temperature: 13.18,
            baseline_mean: 13.1,
            baseline_std_dev_upper: 15.0,
            baseline_std_dev_lower: 11.21,
            baseline_max: 21.09,
            baseline_min: 4.65,
        },
        {
            date: "2024-02-01",
            temperature: 15.98,
            baseline_mean: 16.02,
            baseline_std_dev_upper: 17.77,
            baseline_std_dev_lower: 14.27,
            baseline_max: 23.27,
            baseline_min: 8.29,
        },
        {
            date: "2024-03-01",
            temperature: 18.18,
            baseline_mean: 18.14,
            baseline_std_dev_upper: 19.78,
            baseline_std_dev_lower: 16.5,
            baseline_max: 24.62,
            baseline_min: 11.21,
        },
        {
            date: "2024-04-01",
            temperature: 19.24,
            baseline_mean: 18.93,
            baseline_std_dev_upper: 20.54,
            baseline_std_dev_lower: 17.33,
            baseline_max: 24.8,
            baseline_min: 12.98,
        },
        {
            date: "2024-05-01",
            temperature: 18.44,
            baseline_mean: 18.12,
            baseline_std_dev_upper: 19.77,
            baseline_std_dev_lower: 16.48,
            baseline_max: 24.62,
            baseline_min: 11.18,
        },
        {
            date: "2024-06-01",
            temperature: 16.3,
            baseline_mean: 15.94,
            baseline_std_dev_upper: 17.69,
            baseline_std_dev_lower: 14.19,
            baseline_max: 23.24,
            baseline_min: 8.13,
        },
        {
            date: "2024-07-01",
            temperature: 13.28,
            baseline_mean: 12.96,
            baseline_std_dev_upper: 14.86,
            baseline_std_dev_lower: 11.06,
            baseline_max: 20.97,
            baseline_min: 4.5,
        },
        {
            date: "2024-08-01",
            temperature: 9.83,
            baseline_mean: 9.95,
            baseline_std_dev_upper: 12.01,
            baseline_std_dev_lower: 7.9,
            baseline_max: 18.28,
            baseline_min: 1.36,
        },
        {
            date: "2024-09-01",
            temperature: 7.95,
            baseline_mean: 7.81,
            baseline_std_dev_upper: 9.97,
            baseline_std_dev_lower: 5.65,
            baseline_max: 15.99,
            baseline_min: -0.37,
        },
        {
            date: "2024-10-01",
            temperature: 7.18,
            baseline_mean: 7.07,
            baseline_std_dev_upper: 9.27,
            baseline_std_dev_lower: 4.88,
            baseline_max: 14.79,
            baseline_min: -0.6,
        },
        {
            date: "2024-11-01",
            temperature: 8.12,
            baseline_mean: 7.92,
            baseline_std_dev_upper: 10.07,
            baseline_std_dev_lower: 5.77,
            baseline_max: 16.12,
            baseline_min: -0.3,
        },
        {
            date: "2024-12-01",
            temperature: 10.25,
            baseline_mean: 10.14,
            baseline_std_dev_upper: 12.18,
            baseline_std_dev_lower: 8.1,
            baseline_max: 18.46,
            baseline_min: 1.54,
        },
        {
            date: "2025-01-01",
            temperature: 11.48,
            baseline_mean: 11.57,
            baseline_std_dev_upper: 13.54,
            baseline_std_dev_lower: 9.6,
            baseline_max: 18.48,
            baseline_min: 4.65,
        },
    ],
};
// provide init-options
const renderer = ref<"svg" | "canvas">("svg");
const initOptions = computed(() => ({
    width: "auto",
    height: 600,
    renderer: renderer.value,
}));
provide(INIT_OPTIONS_KEY, initOptions);

const option = ref<ECOption>({
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
        source: data.time_series,
    },
    grid: {
        left: 0,
        right: 0,
        containLabel: true,
    },
    xAxis: {
        type: "time",
    },
    yAxis: {},
    series: [{ type: "line" }],
});
</script>

<template>
    <VChart :option="option" :init-options="initOptions" autoresize />
</template>
