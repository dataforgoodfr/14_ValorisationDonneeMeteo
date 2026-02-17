<template>
    <p>barchart</p>
    <VChart :option="option" autoresize />
</template>

<script setup lang="ts">
import { provide } from "vue";
<<<<<<< feat/#56_GenerateMockupDataFile
import { GetData, type ChartDataSerie } from "~~/public/ChartDataProvider"; // provide init-options
=======
import { GetChartData, TimeAxisType } from "~~/public/ChartDataProvider"; // provide init-options
>>>>>>> main

// provide init-options
const renderer = ref<"svg" | "canvas">("svg");
const initOptions = computed(() => ({
    height: 300,
    renderer: renderer.value,
}));
provide(INIT_OPTIONS_KEY, initOptions);

<<<<<<< feat/#56_GenerateMockupDataFile
let SourceDataSet: ChartDataSerie = [];

let PosDelta = SourceDataSet?.map((item) => {
=======
const Data = GetChartData(TimeAxisType.Day);

const PosDelta = Data.map((item) => {
>>>>>>> main
    if (item.Delta >= 0) {
        return item.Delta;
    } else {
        return "-";
    }
});
<<<<<<< feat/#56_GenerateMockupDataFile
let NegDelta = SourceDataSet?.map((item) => {
=======
const NegDelta = Data.map((item) => {
>>>>>>> main
    if (item.Delta < 0) {
        return item.Delta;
    } else {
        return "-";
    }
});

const option = ref<ECOption>({
<<<<<<< feat/#56_GenerateMockupDataFile
    dataset: {
        source: [PosDelta, NegDelta],
    },
    xAxis: [
        {
            data: SourceDataSet.map((item) => {
=======
    xAxis: [
        {
            data: Data.map((item) => {
>>>>>>> main
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
<<<<<<< feat/#56_GenerateMockupDataFile
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
=======
>>>>>>> main
});
</script>
