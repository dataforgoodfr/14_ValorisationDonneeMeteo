<template>
    <VChart :option="option" autoresize />
</template>

<script setup lang="ts">

import type { TopLevelFormatterParams } from "echarts/types/dist/shared.js";
import { type ChartDataPoint, type ChartDataSerie } from "~~/public/ChartDataProvider";


// provide init-options
const renderer = ref<"svg" | "canvas">("svg");
const initOptions = computed(() => ({
    height: 600,
    renderer: renderer.value,
}));

interface ITNChartDataType extends ChartDataPoint {
    SerieITN: number,
    SerieDelta: number,
    SerieMinStdSDev: number,
    SerieMaxStdDev: number,
    SerieMin: number,
    SerieMax: number,

}

provide(INIT_OPTIONS_KEY, initOptions);
let source: ChartDataSerie = []
let base = 0

const YAxisId = "MainY"

function ShortDate(date: Date) {
    if (date?.getMonth) {
        return [
            date.getMonth() + 1,
            date.getDate(),
            date.getMonth() + 1,
            date.getFullYear(),
        ].join("/");
    }
    else {
        return date
    }
}

function YAxisFormater(val: number) {
    return `${val + base} °C`;
}

const option = ref<ECOption>({

    dataset: {
        dimensions: ["date", "ITN", "Delta", "StdDev", "Min", "Max", "SerieITN"],
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
            return `${ShortDate(item.date)}<br />ITN : ${item.ITN.toFixed(2)}°C`;
        },
    },
    xAxis: [
        {
            type: "category",
            axisLabel: {
                // formatter: function (value: string) {
                //     const date = new Date(value);
                //     return ShortDate(date);
                // },
            },
            boundaryGap: false,
        },
    ],
    yAxis: {
        axisLabel: {
            formatter: YAxisFormater,
        },
        id: YAxisId,
        axisPointer: {
            label: {
                formatter: function (params) {
                    return `${(Number(params.value) - base).toFixed(2)}°c`;
                },
            },
        },
        splitNumber: 3,
    },
    series: [
        {
            name: "SerieITN",
            type: "line",
            // data: source.map(function (item) {
            //     return base + item.ITN;
            // }),
            dimensions: ['date', 'SerieITN'],
            seriesLayoutBy: 'column',
            lineStyle: {
                color: "#130707",
            },
            showSymbol: false,

        },
        {
            name: "SerieDelta",
            type: "line",
            dimensions: ['date', 'SerieDelta'],
            lineStyle: {
                color: "#2d3ed3",
                width: 0.75,
            },
            showSymbol: false,
            yAxisId: YAxisId
        },
        {
            name: "SerieMin",
            type: "line",
            dimensions: ['date', 'SerieMin'],
            stack: "MinMax",
            lineStyle: {
                opacity: 0,
            },
            showSymbol: false,
            yAxisId: YAxisId
        },
        {
            name: "SerieMax",
            type: "line",
            stack: "MinMax",
            dimensions: ['date', 'SerieMax'],
            lineStyle: {
                opacity: 0,
            },
            areaStyle: {
                color: "#777777",
            },
            showSymbol: false,
            yAxisId: YAxisId
        },
        {
            name: "Ldev",
            type: "line",
            dimensions: ['date', 'SerieMinStdDev'],
            stack: "bands",
            lineStyle: {
                opacity: 0,
            },
            showSymbol: false,
            yAxisId: YAxisId
        },

        {
            name: "UDev",
            type: "line",
            dimensions: ['date', 'SerieMaxStdDev'],
            stack: "bands",
            lineStyle: {
                opacity: 0,
            },
            areaStyle: {
                color: "#cccccc",
            },
            showSymbol: false,
            yAxisId: YAxisId
        },
    ],
});

onMounted(async () => {
    const resp = await fetch("MockedUpData.json")
    source = await resp.json() as ITNChartDataType
    base = source.reduce(function (min: number, val: ChartDataPoint) {
        return Math.floor(Math.min(min, val.Min));
    }, Infinity);

    const DataSetSource = source.map((item) => {
        const ItemDate = new Date(Date.parse(item.date))
        return {
            ...item,
            date: ItemDate,
            SerieITN: -base + item.ITN,
            SerieDelta: item.ITN + item.Delta - base,
            SerieMinStdDev: item.ITN - item.StdDev - base,
            SerieMaxStdDev: 2 * item.StdDev,
            SerieMin: -base + item.Min,
            SerieMax: item.Max - item.Min,
        }
    })

    option.value.dataset.source = DataSetSource
    option.value.yAxis.min = 0

})


</script>
