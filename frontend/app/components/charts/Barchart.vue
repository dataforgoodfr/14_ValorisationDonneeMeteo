<template>
  <p>barchart</p>
  <VChart :option="option" autoresize />
</template>

<script setup lang="ts">
import { provide } from "vue";
import { GetChartData, TimeAxisType } from "../../../public/ChartDataProvider"

// provide init-options
const renderer = ref<"svg" | "canvas">("svg");
const initOptions = computed(() => ({
  height: 300,
  renderer: renderer.value,
}));
provide(INIT_OPTIONS_KEY, initOptions);

const Data = GetChartData( TimeAxisType.Day )

const PosDelta = Data.map((item) => {
  if (item.Delta >= 0) {
    return item.Delta
  }
  else {
    return '-'
  }
})
const NegDelta = Data.map((item) => {
  if (item.Delta < 0) {
    return item.Delta
  }
  else {
    return '-'
  }
})

const option = ref<ECOption>({

  xAxis: [{
    data: Data.map((item) => { return (item.date.getDate()) + '/' + (item.date.getMonth()+1) }),
    silent: false,
    splitLine: {
      show: false
    },
    splitArea: {
      show: false
    }
  }],
  yAxis: { type: 'value' },
  series: [
    {
      name: 'Pos',
      type: 'bar',
      label: {
        show: false,
        position: 'top'
      },
      itemStyle: {
        color: 'red'
      }, data: PosDelta,
      large: true
    },
    {
      name: 'Neg',
      type: 'bar',
      label: {
        show: false,
        position: 'bottom'
      },
      itemStyle: {
        color: 'blue'
      },
      data: NegDelta,
      large: true
    }
  ]
});
</script>
