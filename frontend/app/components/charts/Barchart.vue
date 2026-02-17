<template>
    <p>barchart</p>
    <VChart :option="option" autoresize />
</template>

<script setup lang="ts">
import { provide } from "vue";
import { GetData, type ChartDataSerie } from "~~/public/ChartDataProvider"; // provide init-options

// provide init-options
const renderer = ref<"svg" | "canvas">("svg");
const initOptions = computed(() => ({
    height: 300,
    renderer: renderer.value,
}));
provide(INIT_OPTIONS_KEY, initOptions);

let SourceDataSet: ChartDataSerie = [];

let PosDelta = SourceDataSet?.map((item) => {
    if (item.Delta >= 0) {
        return item.Delta;
    } else {
        return "-";
    }
});
let NegDelta = SourceDataSet?.map((item) => {
    if (item.Delta < 0) {
        return item.Delta;
    } else {
        return "-";
    }
});

const option = ref<ECOption>({
    dataset: {
        source: [PosDelta, NegDelta],
    },
    xAxis: [
        {
            data: SourceDataSet.map((item) => {
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

onMounted(async () => {
    SourceDataSet = await GetData();

    PosDelta = SourceDataSet.map((item) => {
        if (item.Delta >= 0) {
            return item.Delta;
        } else {
            return "-";
        }
    });
    NegDelta = SourceDataSet.map((item) => {
        if (item.Delta < 0) {
            return item.Delta;
        } else {
            return "-";
        }
    });

    option.value.xAxis.data = SourceDataSet.map((item) => {
        const itemdate = new Date(Date.parse(item.date));
        return `${itemdate.getDate()}/${itemdate.getMonth() + 1}`;
    });
    option.value.series[0].data = PosDelta;
    option.value.series[1].data = NegDelta;
});
</script>
