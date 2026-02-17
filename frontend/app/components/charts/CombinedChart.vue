<template>
    <VChart :option="option" autoresize />
</template>

<script setup lang="ts">
import type { TopLevelFormatterParams } from "echarts/types/dist/shared.js";
<<<<<<< feat/#56_GenerateMockupDataFile
import {
    GetData,
    type ChartDataPoint,
    type ChartDataSerie,
} from "~~/public/ChartDataProvider";
=======
import { GetChartData, TimeAxisType } from "~~/public/ChartDataProvider";
>>>>>>> main

// provide init-options
const renderer = ref<"svg" | "canvas">("svg");
const initOptions = computed(() => ({
    height: 600,
    renderer: renderer.value,
}));
<<<<<<< feat/#56_GenerateMockupDataFile

interface ITNChartDataType extends ChartDataPoint {
    SerieITN: number;
    SerieDelta: number;
    SerieMinStdSDev: number;
    SerieMaxStdDev: number;
    SerieMin: number;
    SerieMax: number;
}

provide(INIT_OPTIONS_KEY, initOptions);
let source: ChartDataSerie = [];
let base = 0;

const YAxisId = "MainY";

function ShortDate(date: Date) {
    if (date?.getMonth) {
        return [
            date.getMonth() + 1,
            date.getDate(),
            date.getMonth() + 1,
            date.getFullYear(),
        ].join("/");
    } else {
        return date;
    }
}

function YAxisFormater(val: number) {
    return `${val + base} °C`;
}

const option = ref<ECOption>({
    dataset: {
        dimensions: [
            "date",
            "ITN",
            "Delta",
            "StdDev",
            "Min",
            "Max",
            "SerieITN",
        ],
=======
provide(INIT_OPTIONS_KEY, initOptions);

const source = GetChartData(TimeAxisType.Day);
// Compute base to stack
const base = -source.reduce(function (min: number, val: unknown) {
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
>>>>>>> main
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
<<<<<<< feat/#56_GenerateMockupDataFile
            return `${ShortDate(item.date)}<br />ITN : ${item.ITN.toFixed(2)}°C`;
=======
            return `${ShortDate(item.date)}<br />${item.ITN.toFixed(2)}°C`;
>>>>>>> main
        },
    },
    xAxis: [
        {
            type: "category",
<<<<<<< feat/#56_GenerateMockupDataFile
            axisLabel: {
                // formatter: function (value: string) {
                //     const date = new Date(value);
                //     return ShortDate(date);
                // },
=======
            data: source.map(function (item) {
                return item.date;
            }),
            axisLabel: {
                formatter: function (value: string) {
                    const date = new Date(value);
                    return ShortDate(date);
                },
>>>>>>> main
            },
            boundaryGap: false,
        },
    ],
    yAxis: {
        axisLabel: {
<<<<<<< feat/#56_GenerateMockupDataFile
            formatter: YAxisFormater,
        },
        id: YAxisId,
=======
            formatter: function (val: number) {
                return `${val - base} °C`;
            },
        },
>>>>>>> main
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
<<<<<<< feat/#56_GenerateMockupDataFile
            name: "SerieITN",
            type: "line",
            // data: source.map(function (item) {
            //     return base + item.ITN;
            // }),
            dimensions: ["date", "SerieITN"],
            seriesLayoutBy: "column",
=======
            name: "ITN",
            type: "line",
            data: source.map(function (item) {
                return base + item.ITN;
            }),
>>>>>>> main
            lineStyle: {
                color: "#130707",
            },
            showSymbol: false,
        },
        {
<<<<<<< feat/#56_GenerateMockupDataFile
            name: "SerieDelta",
            type: "line",
            dimensions: ["date", "SerieDelta"],
=======
            name: "Delta",
            type: "line",
            data: source.map(function (item) {
                return base + item.ITN + item.Delta;
            }),
>>>>>>> main
            lineStyle: {
                color: "#2d3ed3",
                width: 0.75,
            },
            showSymbol: false,
<<<<<<< feat/#56_GenerateMockupDataFile
            yAxisId: YAxisId,
        },
        {
            name: "SerieMin",
            type: "line",
            dimensions: ["date", "SerieMin"],
=======
        },
        {
            name: "Min",
            type: "line",
            data: source.map(function (item) {
                return base + item.Min;
            }),
>>>>>>> main
            stack: "MinMax",
            lineStyle: {
                opacity: 0,
            },
            showSymbol: false,
<<<<<<< feat/#56_GenerateMockupDataFile
            yAxisId: YAxisId,
        },
        {
            name: "SerieMax",
            type: "line",
            stack: "MinMax",
            dimensions: ["date", "SerieMax"],
=======
        },
        {
            name: "Max",
            type: "line",
            data: source.map(function (item) {
                return item.Max - item.Min;
            }),
            stack: "MinMax",
>>>>>>> main
            lineStyle: {
                opacity: 0,
            },
            areaStyle: {
                color: "#777777",
            },
            showSymbol: false,
<<<<<<< feat/#56_GenerateMockupDataFile
            yAxisId: YAxisId,
=======
>>>>>>> main
        },
        {
            name: "Ldev",
            type: "line",
<<<<<<< feat/#56_GenerateMockupDataFile
            dimensions: ["date", "SerieMinStdDev"],
=======
            data: source.map(function (item) {
                return base + item.ITN - item.StdDev;
            }),
>>>>>>> main
            stack: "bands",
            lineStyle: {
                opacity: 0,
            },
            showSymbol: false,
<<<<<<< feat/#56_GenerateMockupDataFile
            yAxisId: YAxisId,
=======
>>>>>>> main
        },

        {
            name: "UDev",
            type: "line",
<<<<<<< feat/#56_GenerateMockupDataFile
            dimensions: ["date", "SerieMaxStdDev"],
=======
            data: source.map(function (item) {
                return 2 * item.StdDev;
            }),
>>>>>>> main
            stack: "bands",
            lineStyle: {
                opacity: 0,
            },
            areaStyle: {
                color: "#cccccc",
            },
            showSymbol: false,
<<<<<<< feat/#56_GenerateMockupDataFile
            yAxisId: YAxisId,
        },
    ],
});

onMounted(async () => {
    source = (await GetData()) as ITNChartDataType[];
    base = source.reduce(function (min: number, val: ChartDataPoint) {
        return Math.floor(Math.min(min, val.Min));
    }, Infinity);

    const DataSetSource = source.map((item) => {
        const ItemDate = new Date(Date.parse(item.date));
        return {
            ...item,
            date: ItemDate,
            SerieITN: -base + item.ITN,
            SerieDelta: item.ITN + item.Delta - base,
            SerieMinStdDev: item.ITN - item.StdDev - base,
            SerieMaxStdDev: 2 * item.StdDev,
            SerieMin: -base + item.Min,
            SerieMax: item.Max - item.Min,
        };
    });

    option.value.dataset.source = DataSetSource;
    option.value.yAxis.min = 0;
});
=======
        },
    ],
});
>>>>>>> main
</script>
