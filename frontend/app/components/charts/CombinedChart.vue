<template>
  <VChart :option="option" autoresize />
</template>

<script setup lang="ts">
import type { TopLevelFormatterParams } from "echarts/types/dist/shared.js";
import { GetChartData, TimeAxisType } from "~~/public/ChartDataProvider";


// provide init-options
const renderer = ref<"svg" | "canvas">("svg");
const initOptions = computed(() => ({
  height: 600,
  renderer: renderer.value,
}));
provide(INIT_OPTIONS_KEY, initOptions);

const source = GetChartData(TimeAxisType.Day);
// Compute base to stack
const base = -source.reduce(function (min:number, val:unknown) {
  return Math.floor(Math.min(min, val.Min));
}, Infinity);

function ShortDate(date: Date) {
  return [
    date.getMonth() + 1,
    date.getDate(),
    date.getMonth() + 1,
    date.getFullYear(),
  ].join("/");
}
const option = ref<ECOption>({
  dataset: {
    dimensions: ["date", "ITN", "StdDev"],
    source: source,
  },
  tooltip: {
    trigger: "axis",
    axisPointer: {
      type: "cross",
      animation: false,
      label: {
        backgroundColor: "#ccc",
        borderColor: "#aaa",
        borderWidth: 1,
        shadowBlur: 0,
        shadowOffsetX: 0,
        shadowOffsetY: 0,
        color: "#222",
      },
    },
    formatter: function (params: TopLevelFormatterParams) {
      const first = Array.isArray(params) ? params[0] : params;
      if (!first) return "";
      const item = source[first.dataIndex];
      if (!item) return "";
      return (
        ShortDate(item.date) +
        "<br />" +
        item.ITN.toFixed(2) +
        "°C"
      );
    },
  },
  xAxis: [{
    type: "category",
    data: source.map(function (item) {
      return item.date;
    }),
    axisLabel: {
      formatter: function (value: string, idx: number) {
        const date = new Date(value);
        return ShortDate(date);
      },
    },
    boundaryGap: false,
  }],
  yAxis: {
    axisLabel: {
      formatter: function (val: number) {
        return val - base + " °C";
      },
    },
    axisPointer: {
      label: {
        formatter: function (params) {
          return (Number(params.value) - base).toFixed(2) + "°c";
        },
      },
    },
    splitNumber: 3,
  },
  series: [
    {
      name: "ITN",
      type: "line",
      data: source.map(function (item) {
        return base + item.ITN;
      }),
      lineStyle: {
        color: "#130707",
      },
      showSymbol: false,
    },
    {
      name: "Delta",
      type: "line",
      data: source.map(function (item) {
        return base + item.ITN + item.Delta;
      }),
      lineStyle: {
        color: "#2d3ed3",
        width: 0.75,
      },
      showSymbol: false,
    },
    {
      name: "Min",
      type: "line",
      data: source.map(function (item) {
        return base + item.Min;
      }),
      stack: "MinMax",
      lineStyle: {
        opacity: 0,
      },
      showSymbol: false,
    },
    {
      name: "Max",
      type: "line",
      data: source.map(function (item) {
        return item.Max - item.Min;
      }),
      stack: "MinMax",
      lineStyle: {
        opacity: 0,
      },
      areaStyle: {
        color: "#777777",
      },
      showSymbol: false,
    },
    {
      name: "Ldev",
      type: "line",
      data: source.map(function (item) {
        return base + item.ITN - item.StdDev;
      }),
      stack: "bands",
      lineStyle: {
        opacity: 0,
      },
      showSymbol: false,
    },

    {
      name: "UDev",
      type: "line",
      data: source.map(function (item) {
        return 2 * item.StdDev;
      }),
      stack: "bands",
      lineStyle: {
        opacity: 0,
      },
      areaStyle: {
        color: "#cccccc",
      },
      showSymbol: false,
    },
  ],
});



</script>
