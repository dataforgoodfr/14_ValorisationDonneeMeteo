<script setup lang="ts">
import * as echarts from "echarts/core";
import langFR from "~/i18n/langFR.js";
import type { SelectBarAdapter } from "~/components/ui/commons/selectBar/types";
import type { TemperatureRecordsGraphResponse } from "~/types/api";
import {
    DataZoomComponent,
    GridComponent,
    LegendComponent,
    TitleComponent,
    TooltipComponent,
} from "echarts/components";
import { BarChart, ScatterChart } from "echarts/charts";
import { CanvasRenderer } from "echarts/renderers";
import { UniversalTransition } from "echarts/features";
import { recordsChartTooltipFormatter } from "~/components/charts/tooltipFormatters/recordsChartTooltipFormatter";
import {
    barSeries,
    buildTerritoryPlots,
    countByPeriod,
    periodKey,
    scatterSeries,
} from "~/utils/recordsChartUtils";
import { dateToStringYMD } from "~/utils/date";
import { useMapColors } from "~/constants/colors";
import { FONT_CHARTS, GRAPH_RECORDS_POSITION } from "~/constants/fonts";
import { xAxisTimeFormatter } from "~/utils/chartAxisFormatter";

echarts.registerLocale("FR", langFR);
echarts.use([
    GridComponent,
    TitleComponent,
    TooltipComponent,
    LegendComponent,
    DataZoomComponent,
    ScatterChart,
    BarChart,
    CanvasRenderer,
    UniversalTransition,
]);

interface Props {
    adapter: SelectBarAdapter<TemperatureRecordsGraphResponse>;
}

const props = defineProps<Props>();

const mapColors = useMapColors();
// provide init-options
const renderer = ref<"svg" | "canvas">("canvas");
const initOptions = computed(() => ({
    height: GRAPH_RECORDS_POSITION.height,
    locale: "FR",
    renderer: renderer.value,
}));
provide(INIT_OPTIONS_KEY, initOptions);

const option = computed<ECOption>(() => {
    const data = props.adapter.data.value;
    if (!data) return {};

    const selectedTerritories = props.adapter.selectedElements?.value ?? [];
    const selectedCount = selectedTerritories.length;
    const showStackedBar = selectedCount <= 1;

    const territoryPlots = buildTerritoryPlots(selectedTerritories, data);

    const plots = showStackedBar
        ? ["scatter", "bar"]
        : territoryPlots.map(() => "scatter");

    const barDataset = () => {
        const first = territoryPlots[0];
        if (!first) return [];
        const granularity = props.adapter.granularity.value;
        const hotByPeriod = countByPeriod(first.hot, granularity);
        const coldByPeriod = countByPeriod(first.cold, granularity);

        // Génère tous les buckets du range pour qu'ECharts calcule une largeur
        // de barre d'1 période au lieu d'auto-scaler sur les rares points réels.
        const allPeriodKeys: string[] = [];
        const currentDate = new Date(props.adapter.pickedDateStart.value);
        // Comparaison en chaîne "YYYY-MM-DD" pour ignorer la composante heure :
        // pickedDateStart/End peuvent être créés à l'heure courante (pas minuit),
        // ce qui décalerait la borne de la boucle de quelques ms.
        const dateEndStr = dateToStringYMD(props.adapter.pickedDateEnd.value);
        while (dateToStringYMD(currentDate) <= dateEndStr) {
            allPeriodKeys.push(
                periodKey(dateToStringYMD(currentDate), granularity),
            );
            if (granularity === "year")
                currentDate.setFullYear(currentDate.getFullYear() + 1);
            else if (granularity === "month")
                currentDate.setMonth(currentDate.getMonth() + 1);
            else currentDate.setDate(currentDate.getDate() + 1);
        }

        // ECharts centre les barres sur le timestamp du point. Pour que la barre
        // de l'année/mois N occupe visuellement la bonne période, on positionne
        // chaque barre au milieu de sa période (juillet pour une année, 16 pour un mois).
        const periodMidpointUTC = (key: string): number => {
            const [year, month, day] = key.split("-").map(Number);
            if (granularity === "year") return Date.UTC(year!, 6, 2);
            if (granularity === "month") return Date.UTC(year!, month! - 1, 16);
            return Date.UTC(year!, month! - 1, day!);
        };

        return [
            {
                dimensions: ["period", "x", "hot", "cold"],
                source: allPeriodKeys.map((period) => ({
                    period,
                    x: periodMidpointUTC(period),
                    hot: hotByPeriod[period] ?? 0,
                    cold: coldByPeriod[period] ?? 0,
                })),
            },
        ];
    };

    return {
        dataset: [
            ...territoryPlots.flatMap((territory) => [
                {
                    dimensions: ["date", "value", "station"],
                    source: territory.hot,
                },
                {
                    dimensions: ["date", "value", "station"],
                    source: territory.cold,
                },
            ]),
            ...(showStackedBar ? barDataset() : []),
        ],
        grid: plots.map((plot, index) => {
            if (!showStackedBar) {
                return {
                    top: `${index * (100 / plots.length) + 8}%`,
                    height: `${100 / plots.length - 15}%`,
                    left: 60,
                    right: 10,
                };
            }

            if (plot === "scatter") {
                return { top: "8%", height: "55%", left: 60, right: 10 };
            }
            return { top: "72%", height: "20%", left: 60, right: 10 };
        }),
        xAxis: plots.map((_, index) => ({
            type: "time",
            gridIndex: index,
            // Date.UTC avec les composantes locales évite le décalage timezone :
            // le date picker crée des dates à minuit LOCAL (ex. 1er mai 00:00 CEST
            // = 30 avril 22:00 UTC). Utiliser .getTime() directement donnerait un
            // max différent entre scatter et bar, ECharts auto-étendant l'axe bar
            // pour loger la dernière barre → les deux grilles se désaligneraient.
            min: () => {
                const startDate = props.adapter.pickedDateStart?.value;
                if (!startDate) return Date.now();
                return Date.UTC(
                    startDate.getFullYear(),
                    startDate.getMonth(),
                    startDate.getDate(),
                );
            },
            max: () => {
                const endDate = props.adapter.pickedDateEnd?.value;
                if (!endDate) return Date.now();
                const granularity = props.adapter.granularity.value;
                if (granularity === "year")
                    return Date.UTC(endDate.getFullYear() + 1, 0, 1);
                if (granularity === "month")
                    return Date.UTC(
                        endDate.getFullYear(),
                        endDate.getMonth() + 1,
                        1,
                    );
                return Date.UTC(
                    endDate.getFullYear(),
                    endDate.getMonth(),
                    endDate.getDate() + 1,
                );
            },
            nameLocation: "middle",
            nameGap: 25,
            nameTextStyle: {
                fontSize: FONT_CHARTS.axisName,
                fontWeight: "bold",
            },
            axisPointer: { type: "line", label: { show: false } },
            boundaryGap: ["3%", "3%"],
            axisLabel: {
                formatter: xAxisTimeFormatter(props.adapter.granularity.value),
            },
        })),
        yAxis: plots.map((plot, index) => ({
            type: "value",
            gridIndex: index,
            splitNumber: 3,
            name: plot === "bar" ? "Nombre de records" : "Température (°C)",
            nameRotate: 90,
            nameLocation: "middle",
            nameGap: 40,
            nameTextStyle: {
                fontSize: FONT_CHARTS.axisName,
                fontWeight: "bold",
            },
            axisLabel: { fontSize: FONT_CHARTS.axis },
            splitLine: {
                lineStyle: { type: "dashed", color: mapColors.value.splitLine },
            },
        })),
        series: [
            ...territoryPlots.flatMap((_, index) => [
                scatterSeries({
                    name: "Records de chaleur",
                    datasetIndex: index * 2,
                    encode: { x: "date", y: "value" },
                    color: mapColors.value.hot,
                    symbolSize: 5,
                    xAxisIndex: index,
                    yAxisIndex: index,
                }),
                scatterSeries({
                    name: "Records de froid",
                    datasetIndex: index * 2 + 1,
                    encode: { x: "date", y: "value" },
                    color: mapColors.value.cold,
                    symbolSize: 5,
                    xAxisIndex: index,
                    yAxisIndex: index,
                }),
            ]),
            ...(showStackedBar
                ? (["hot", "cold"] as const).map((type) =>
                      barSeries({
                          name:
                              type === "hot"
                                  ? "Records de chaleur"
                                  : "Records de froid",
                          datasetIndex: territoryPlots.length * 2,
                          encode: { x: "x", y: type },
                          color: mapColors.value[type],
                          stack: "records",
                          xAxisIndex: 1,
                          yAxisIndex: 1,
                      }),
                  )
                : []),
        ],
        title: territoryPlots.map((plot, index) => ({
            text: plot.name,
            right: "right",
            top: showStackedBar ? "2%" : `${index * (100 / plots.length) + 2}%`,
        })),
        axisPointer: {
            link: [{ xAxisIndex: "all" }],
            label: { backgroundColor: mapColors.value.chartAccentColor },
        },
        legend: {
            data: ["Records de chaleur", "Records de froid"],
            bottom: -5,
        },
        tooltip: {
            trigger: "item",
            axisPointer: { type: "cross" },
            borderColor: "transparent",
            formatter: (params) =>
                recordsChartTooltipFormatter(
                    params,
                    props.adapter.granularity.value,
                ),
        },
        dataZoom: [
            {
                type: "inside",
                xAxisIndex: plots.map((_, i) => i),
                minSpan: 20,
            },
        ],
    };
});
</script>

<template>
    <VChart
        :ref="adapter.chartRef"
        :key="`${adapter.granularity.value}-${adapter.selectedElements?.value?.map((e) => e.id).join('-')}`"
        :option="option"
        :init-options="initOptions"
        :loading="adapter.pending.value"
        :loading-options="{
            text: 'Chargement…',
            color: mapColors.loadingSpinColor,
        }"
        autoresize
    />
</template>
