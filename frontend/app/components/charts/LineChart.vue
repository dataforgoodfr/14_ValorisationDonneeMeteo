<template>
    <p>linechart</p>
    <VChart :option="option" autoresize />
</template>

<script setup lang="ts">
import { provide } from "vue";
import {  type ChartDataSerie } from "~~/public/ChartDataProvider";

// provide init-options
const renderer = ref<"svg" | "canvas">("svg");
const initOptions = computed(() => ({
    height: 300,
    renderer: renderer.value,
}));
provide(INIT_OPTIONS_KEY, initOptions);

let SourceDataSet:ChartDataSerie=[]

const option = ref<ECOption>({
    dataset: {
        dimensions: ["date", "Delta"],
        source: SourceDataSet,
    },
    xAxis: {
        type: "time",
    },
    yAxis: {},
    series: [{ type: "line", showSymbol: false }],
});

    onMounted(  async ()=> {
        const resp = await fetch ("MockedUpData.json")
        SourceDataSet = await resp.json()
        
        option.value.dataset.source = SourceDataSet})
</script>
