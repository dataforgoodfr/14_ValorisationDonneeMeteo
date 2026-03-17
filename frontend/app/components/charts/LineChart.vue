<script setup lang="ts">
import { INIT_OPTIONS_KEY } from "vue-echarts";
import { provide } from "vue";

const deviationStore = useDeviationStore();
const { chartRef } = storeToRefs(deviationStore);

// provide init-options
const renderer = ref<"svg" | "canvas">("svg");
const initOptions = computed(() => ({
    height: 300,
    renderer: renderer.value,
}));
provide(INIT_OPTIONS_KEY, initOptions);

const deviationData = deviationStore.data;

const option = ref<ECOption>({
    dataset: {
        dimensions: ["date", "Delta"],
        source: deviationData,
    },
    xAxis: {
        type: "time",
    },
    yAxis: {},
    series: [{ type: "line", showSymbol: false }],
});
</script>

<template>
    <VChart ref="chartRef" :option="option" autoresize />
</template>
