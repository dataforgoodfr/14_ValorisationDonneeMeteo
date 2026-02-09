<template>
  <p>linechart</p>
  <VChart :option="option" autoresize />
</template>

<script setup lang="ts">
import { provide } from "vue";

// provide init-options
const renderer = ref<"svg" | "canvas">("svg");
const initOptions = computed(() => ({
  height: 300,
  renderer: renderer.value,
}));
provide(INIT_OPTIONS_KEY, initOptions);

const option = ref<ECOption>({
  dataset: {
    dimensions: ["Year", "Matcha Latte"],
    source: [
      { Year: "2015", "Matcha Latte": 54 },
      { Year: "2016", "Matcha Latte": 42 },
      { Year: "2017", "Matcha Latte": 23 },
    ],
  },
  xAxis: { type: "category" },
  yAxis: {},
  series: [{ type: "line" }],
});
</script>
