import type {
    EChartsOption,
    TooltipComponentFormatterCallbackParams,
} from "echarts";
import type { TemperatureRecordsResponse } from "~/types/api";
import { recordsPyramidTooltipFormatter } from "~/components/charts/tooltipFormatters/recordsPyramidTooltipFormatter";
import type {
    XAXisOption,
    YAXisOption,
    GridOption,
    BarSeriesOption,
    TitleOption,
} from "echarts/types/dist/shared";

type Granularity = "year" | "month" | "day";

// ── Formatage de la clé de regroupement selon la granularité ─────────────────
function dateToCategory(isoDate: string, granularity: Granularity): string {
    const parts = isoDate.split("-");
    const y = parts[0] ?? "";
    const m = parts[1] ?? "";
    const d = parts[2] ?? "";
    if (granularity === "year") return y;
    if (granularity === "month") return `${m}/${y}`;
    return `${d}/${m}/${y}`;
}

// ── Construction de l'option ECharts ─────────────────────────────────────────
export function useRecordsPyramidOption(
    data: TemperatureRecordsResponse,
    granularity: Granularity,
): EChartsOption {
    // 1. Catégories triées sans doublons
    const allDates = data.stations.flatMap((s) => [
        ...s.hot_records.map((r) => r.date),
        ...s.cold_records.map((r) => r.date),
    ]);
    const categories = [
        ...new Set(allDates.map((d) => dateToCategory(d, granularity))),
    ].sort();

    // 2. Layout dynamique selon le nombre de stations
    const stationCount = data.stations.length;
    const totalHeightPercentage = 88;
    const gapBetweenPercentage = stationCount === 1 ? 0 : 6;
    const blockHeightPercentage =
        (totalHeightPercentage - (stationCount - 1) * gapBetweenPercentage) /
        stationCount;
    const topOffsetPercentage = 6;

    const grids: GridOption[] = [];
    const xAxes: XAXisOption[] = [];
    const yAxes: YAXisOption[] = [];
    const series: BarSeriesOption[] = [];
    const titles: TitleOption[] = [];

    const labelInterval = granularity === "year" ? 0 : 0;
    const labelFontSize = granularity === "year" ? 12 : 12;

    data.stations.forEach((station, i) => {
        const top =
            topOffsetPercentage +
            i * (blockHeightPercentage + gapBetweenPercentage);
        const bottom = 100 - top - blockHeightPercentage;
        const leftGridIndex = i * 2; // grille gauche = froids
        const rightGridIndex = i * 2 + 1; // grille droite = chauds

        // 3. Comptages réels par catégorie
        const hotCounts = categories.map(
            (cat) =>
                station.hot_records.filter(
                    (r) => dateToCategory(r.date, granularity) === cat,
                ).length,
        );
        const coldCounts = categories.map(
            (cat) =>
                station.cold_records.filter(
                    (r) => dateToCategory(r.date, granularity) === cat,
                ).length,
        );

        // 4. Grids
        const labelColWidth =
            granularity === "year" ? 56 : granularity === "month" ? 57 : 58; // en %
        const marginWidth =
            granularity === "year" ? 27 : granularity === "month" ? 31 : 35; // en %

        const leftrightGridIndexight = `${labelColWidth}%`; // ex: 48% / 46.5% / 45%
        const rightleftGridIndexeft = `${50}%`; // ex: 48% / 46.5% / 45%

        // Dans le forEach :
        grids.push(
            {
                top: `${top}%`,
                bottom: `${bottom}%`,
                left: "5%",
                right: leftrightGridIndexight,
            },
            {
                top: `${top}%`,
                bottom: `${bottom}%`,
                left: rightleftGridIndexeft,
                right: "4%",
            },
        );

        // 5. Axes X (valeurs, un par grille)
        const xAxisBase: XAXisOption = {
            type: "value",
            min: 0,
            minInterval: 1,
            axisLabel: {
                color: "#000000",
                fontSize: labelFontSize,
                formatter: (v: number) => String(v),
            },
            axisLine: { show: false },
            axisTick: { show: false },
            splitLine: { lineStyle: { color: "#b4b4b4", type: "dashed" } },
        };
        xAxes.push(
            { ...xAxisBase, gridIndex: leftGridIndex, inverse: true },
            { ...xAxisBase, gridIndex: rightGridIndex, inverse: false },
        );

        // 6. Axes Y (catégories, un par grille)
        yAxes.push(
            // Gauche : labels cachés (l'axe du milieu sert de séparateur visuel)
            {
                type: "category",
                gridIndex: leftGridIndex,
                data: categories,
                position: "right",
                axisPointer: { type: "shadow" },
                axisLabel: { show: false },
                axisTick: { show: false },
                axisLine: { show: true },
                splitLine: { show: false },
            },
            // Droite : labels visibles (position centrale entre les deux grilles)
            {
                type: "category",
                gridIndex: rightGridIndex,
                data: categories,
                position: "left",
                axisPointer: { type: "shadow" },
                axisLabel: {
                    color: "#000000",
                    fontSize: labelFontSize,
                    interval: labelInterval,
                    margin: marginWidth,
                    align: "center",
                },
                axisTick: { show: false },
                axisLine: { lineStyle: { color: "#3a5080", width: 1 } },
                splitLine: { show: false },
            },
        );

        // 7. Titre de la station
        titles.push(
            {
                text: station.name,
                top: `${top - 4}%`,
                left: "85%",
                textStyle: {
                    fontSize: labelFontSize,
                    fontWeight: "bold",
                    color: "#000000",
                },
            },
            {
                text: "Nombre de records", // ← nouveau
                top: `${top + blockHeightPercentage + 3}%`, // bas du bloc
                left: "46%", // centré entre les deux grilles
                textAlign: "center",
                textStyle: { fontSize: labelFontSize, color: "#000000" },
            },
        );

        // 8. Séries
        series.push(
            {
                name: `Froids · ${station.name}`,
                type: "bar",
                xAxisIndex: leftGridIndex,
                yAxisIndex: leftGridIndex,
                barMaxWidth: 12,
                data: coldCounts,
                itemStyle: { color: "#1976d2", opacity: 0.85 },
            },
            {
                name: `Chauds · ${station.name}`,
                type: "bar",
                xAxisIndex: rightGridIndex,
                yAxisIndex: rightGridIndex,
                barMaxWidth: 12,
                data: hotCounts,
                itemStyle: { color: "#d32f2f", opacity: 0.85 },
            },
        );
    });

    return {
        backgroundColor: "#ffffff",
        title: titles,
        axisPointer: {
            link: [{ yAxisIndex: "all" }], // lie tous les yAxes
        },
        tooltip: {
            trigger: "axis",
            axisPointer: { type: "shadow" },
            backgroundColor: "#ffffff",
            borderColor: "#ffffff",
            textStyle: { color: "#000000", fontSize: labelFontSize },
            formatter: recordsPyramidTooltipFormatter,
        },
        grid: grids,
        xAxis: xAxes,
        yAxis: yAxes,
        series,
        formatter: recordsPyramidTooltipFormatter as (
            params: TooltipComponentFormatterCallbackParams,
        ) => string,
    };
}
