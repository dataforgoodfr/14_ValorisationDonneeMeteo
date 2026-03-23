<script setup lang="ts">
import * as echarts from "echarts/core";
import langFR from "~/i18n/langFR.js";
import {
    TitleComponent,
    TooltipComponent,
    GridComponent,
    DataZoomComponent,
    LegendComponent,
} from "echarts/components";
import { UniversalTransition } from "echarts/features";
import { CanvasRenderer } from "echarts/renderers";
echarts.registerLocale("FR", langFR);
echarts.use([
    TitleComponent,
    TooltipComponent,
    GridComponent,
    LegendComponent,
    DataZoomComponent,
    UniversalTransition,
    CanvasRenderer,
]);

const deviationStore = useDeviationStore();

// provide init-options
const renderer = ref<"svg" | "canvas">("canvas");
const initOptions = computed(() => ({
    height: 600,
    locale: "FR",
    renderer: renderer.value,
}));
provide(INIT_OPTIONS_KEY, initOptions);

const option = computed<ECOption>(() => {
    const nationalData = deviationStore.deviationData?.national?.data ?? [];
    const title = "Moyenne nationale";

    return {
        dataset: {
            dimensions: [
                "date",
                "deviation",
                "deviation_positive",
                "deviation_negative",
            ],
            source: nationalData.map((p) => ({
                date: p.date,
                deviation: p.deviation,
                deviation_positive: p.deviation >= 0 ? p.deviation : null,
                deviation_negative: p.deviation < 0 ? p.deviation : null,
            })),
        },
        grid: {
            left: 30,
            right: 10,
            bottom: 150,
            containLabel: true,
        },
        xAxis: {
            type: "time",
            axisTick: { show: false },
            nameLocation: "middle",
            nameGap: 25,
            nameTextStyle: { fontSize: 11, fontWeight: "bold" },
            axisPointer: { type: "shadow", label: { show: false } },
        },
        yAxis: {
            type: "value",
            splitNumber: 3,
            name: "Écart à la normale (°C)",
            nameLocation: "middle",
            nameGap: 55,
            nameTextStyle: { fontSize: 10, fontWeight: "bold" },
            axisLabel: { fontSize: 10 },
            splitLine: { lineStyle: { type: "dashed" } },
        },
        series: [
            {
                name: "Ecart positif",
                type: "bar",
                stack: "deviation",
                encode: { x: "date", y: "deviation_positive" },
                color: "#d32f2f",
                tooltip: { show: true },
            },
            {
                name: "Ecart négatif",
                type: "bar",
                stack: "deviation",
                encode: { x: "date", y: "deviation_negative" },
                color: "#1976d2",
                tooltip: { show: true },
            },
        ],
        title: {
            text: title,
            top: "1%",
            right: "3%",
            textStyle: { fontSize: 14, fontWeight: "bold" },
        },
        legend: {
            data: ["Ecart positif", "Ecart négatif"],
            bottom: 85,
        },
        tooltip: {
            trigger: "axis",
            axisPointer: { type: "shadow" },
            formatter: (params) => {
                if (!Array.isArray(params)) return "";
                const [first] = params;
                if (!first) return "";

                const d = first.value as Record<string, number | string>;
                const fmt = (v: number) => `${v.toFixed(2)}°C`;
                const find = (name: string) =>
                    params.find((p) => p.seriesName === name);

                const dateOptions: Intl.DateTimeFormatOptions =
                    deviationStore.granularity === "month"
                        ? { year: "numeric", month: "long" }
                        : deviationStore.granularity === "year"
                          ? { year: "numeric" }
                          : {
                                weekday: "short",
                                day: "numeric",
                                month: "short",
                                year: "numeric",
                            };

                const formattedDate = new Date(
                    d.date as string,
                ).toLocaleDateString("fr-FR", dateOptions);

                const deviation = (d.deviation_positive ??
                    d.deviation_negative) as number;
                const serie =
                    deviation >= 0
                        ? find("Ecart positif")
                        : find("Ecart négatif");
                const sign = deviation >= 0 ? "+" : "";

                return [
                    formattedDate,
                    `${serie?.marker ?? ""}${title} : ${sign}${fmt(deviation)}`,
                ].join("<br/>");
            },
        },
        dataZoom: [
            {
                type: "slider",
                minSpan: 20,
                showDataShadow: false,
            },
            {
                type: "inside",
                minSpan: 20,
            },
        ],
    };
});
</script>

<template>
    <VChart
        :option="option"
        :init-options="initOptions"
        :loading="deviationStore.pending"
        autoresize
    />
</template>
