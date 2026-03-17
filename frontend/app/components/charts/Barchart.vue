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

const PosDelta = deviationData.map((item) => {
    if (item.Delta >= 0) {
        return item.Delta;
    } else {
        return "-";
    }
});
const NegDelta = deviationData.map((item) => {
    if (item.Delta < 0) {
        return item.Delta;
    } else {
        return "-";
    }
});

const option = ref<ECOption>({
    xAxis: [
        {
            data: deviationData.map((item) => {
                return `${item.date.getDate()}/${item.date.getMonth() + 1}`;
            }),
            silent: false,
            splitLine: {
                show: false,
            },
            splitArea: {
                show: false,
            },
        },
    ],
    yAxis: { type: "value" },
    series: [
        {
            name: "Pos",
            type: "bar",
            label: {
                show: false,
                position: "top",
            },
            itemStyle: {
                color: "red",
            },
            data: PosDelta,
            large: true,
        },
        {
            name: "Neg",
            type: "bar",
            label: {
                show: false,
                position: "bottom",
            },
            itemStyle: {
                color: "blue",
            },
            data: NegDelta,
            large: true,
        },
    ],
});
</script>

<template>
    <VChart ref="chartRef" :option="option" autoresize />
</template>
