<template>
  <p>linechart</p>
  <VChart :option="option" autoresize />
</template>

<script setup lang="ts">
import { provide } from "vue";
import { GetChartData, TimeAxisType } from "~~/public/ChartDataProvider";


// provide init-options
const renderer = ref<"svg" | "canvas">("svg");
const initOptions = computed(() => ({
  height: 300,
  renderer: renderer.value,
}));
provide(INIT_OPTIONS_KEY, initOptions);

const Data = GetChartData(TimeAxisType.Day)


const option = ref<ECOption>({
  dataset: {
    dimensions: ["date", "Delta"],
    source: Data,
  },
  xAxis: {
    type: "time",
  },
  yAxis: {},
  series: [{ type: "line", showSymbol: false, }],
});
</script>
