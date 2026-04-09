import type { DeviationResponse } from "~/types/api";
import type { GranularityType } from "~/components/ui/commons/selectBar/types";
import { deviationCalendarTooltipFormatter } from "../components/charts/tooltipFormatters/deviationCalendarTooltipFormatter";
import type { AxisCallbackParams } from "../components/charts/tooltipFormatters/deviationCalendarTooltipFormatter";

const moisFR = [
    "Jan",
    "Fév",
    "Mar",
    "Avr",
    "Mai",
    "Jun",
    "Jul",
    "Aoû",
    "Sep",
    "Oct",
    "Nov",
    "Déc",
];
function buildCategories(
    data: DeviationResponse,
    granularity: GranularityType,
): { xCategories: string[]; yCategories: string[] } {
    const allDates = [
        ...(data.national?.data?.map((d) => d.date) ?? []),
        ...data.stations.flatMap((s) => s.data?.map((d) => d.date) ?? []),
    ];

    if (granularity === "year") {
        // API a renvoyé month → x = années, y = mois
        const years = [...new Set(allDates.map((d) => d.slice(0, 4)))].sort();
        return { xCategories: years, yCategories: moisFR };
    } else {
        // API a renvoyé day → x = mois-année, y = jours
        const monthSet = [
            ...new Set(
                allDates.map((d) => {
                    const [y, m] = d.split("-");
                    return `${moisFR[parseInt(m!) - 1]}-${y!.slice(2)}`;
                }),
            ),
        ].sort((a, b) => {
            const [mA, yA] = a.split("-");
            const [mB, yB] = b.split("-");
            const idxA = moisFR.indexOf(mA!) + parseInt(`20${yA}`) * 12;
            const idxB = moisFR.indexOf(mB!) + parseInt(`20${yB}`) * 12;
            return idxA - idxB;
        });
        return {
            xCategories: monthSet,
            yCategories: Array.from({ length: 31 }, (_, i) => String(i + 1)),
        };
    }
}

function dateToXY(
    isoDate: string,
    granularity: GranularityType,
    xCategories: string[],
): [number, number] | null {
    const [y, m, d] = isoDate.split("-");

    if (granularity === "year") {
        const xi = xCategories.indexOf(y!);
        const yi = parseInt(m!) - 1;
        return xi === -1 ? null : [xi, yi];
    } else {
        const xLabel = `${moisFR[parseInt(m!) - 1]}-${y!.slice(2)}`;
        const xi = xCategories.indexOf(xLabel);
        const yi = parseInt(d!) - 1;
        return xi === -1 ? null : [xi, yi];
    }
}

export function useDeviationCalendarOption(
    data: DeviationResponse,
    granularity: GranularityType,
    stationsNames: string[],
    includeNational: boolean,
) {
    const stationsAndNational = includeNational
        ? [data.national, ...data.stations]
        : data.stations;

    const n = stationsAndNational.length || 1;
    const { xCategories, yCategories } = buildCategories(data, granularity);
    console.log("xCategories:", xCategories);
    console.log("yCategories:", yCategories);

    const VM_MIN = -4;
    const VM_MAX = 5;
    const totalPct = 92;
    const gapPct = n === 1 ? 0 : 8;
    const heatH = (totalPct - (n - 1) * gapPct) / n;
    const topOff = 3;

    const grids: object[] = [];
    const xAxes: object[] = [];
    const yAxes: object[] = [];
    const series: object[] = [];
    const titles: object[] = [];

    const labelInterval = granularity === "year" ? 0 : 1;
    const labelRotate = granularity === "year" ? 0 : 45;
    const xAxisName = granularity === "year" ? "Mois" : "Mois";
    const yAxisName = granularity === "year" ? "Année" : "Jour";

    stationsAndNational.forEach((stationOrNational, i) => {
        const top = topOff + i * (heatH + gapPct);
        const bottom = 100 - top - heatH;

        const heatData = (stationOrNational?.data ?? [])
            .map((p) => {
                const xy = dateToXY(p.date, granularity, xCategories);
                if (!xy) return null;
                return [...xy, p.deviation] as [number, number, number];
            })
            .filter(Boolean) as [number, number, number][];
        console.log("heatData sample:", heatData.slice(0, 5));
        grids.push({
            top: `${top}%`,
            bottom: `${bottom}%`,
            left: "7%",
            right: "12%",
        });

        xAxes.push({
            type: "category",
            gridIndex: i,
            data: xCategories,
            splitArea: { show: true },
            axisTick: { show: false },
            axisLine: { lineStyle: { color: "#3a5080" } },
            axisLabel: {
                color: "#000",
                fontSize: 11,
                interval: labelInterval,
                rotate: labelRotate,
            },
            name: i === n - 1 ? xAxisName : "",
            nameLocation: "middle",
            nameGap: granularity === "year" ? 25 : 38,
            nameTextStyle: { color: "#000", fontSize: 12, fontWeight: "bold" },
        });

        yAxes.push({
            type: "category",
            gridIndex: i,
            data: yCategories,
            splitArea: { show: true },
            axisTick: { show: false },
            axisLine: { lineStyle: { color: "#3a5080" } },
            axisLabel: { color: "#000", fontSize: 11 },
            name: yAxisName,
            nameLocation: "middle",
            nameGap: 35,
            nameTextStyle: { color: "#000", fontSize: 12, fontWeight: "bold" },
        });

        titles.push({
            text: stationsNames[i] ?? "",
            top: `${top - 4}%`,
            left: "7%",
            textStyle: { fontSize: 12, fontWeight: "bold", color: "#000" },
        });

        series.push({
            name: stationsNames[i] ?? "",
            type: "heatmap",
            xAxisIndex: i,
            yAxisIndex: i,
            data: heatData,
            label: { show: false },
            emphasis: {
                itemStyle: { shadowBlur: 10, shadowColor: "rgba(0,0,0,0.5)" },
            },
        });
    });

    return {
        title: titles,
        tooltip: {
            formatter: (params: unknown) =>
                deviationCalendarTooltipFormatter(
                    [params as AxisCallbackParams],
                    granularity,
                    stationsNames,
                ),
        },
        visualMap: stationsAndNational.map((_, i) => ({
            min: VM_MIN,
            max: VM_MAX,
            calculable: i === 0,
            show: i === 0,
            orient: "vertical",
            right: "0%",
            bottom: "center",
            inRange: { color: ["#1976d2", "#ffffff", "#d32f2f"] },
            textStyle: { color: "#000" },
            handleStyle: { borderColor: "#3a5080" },
            seriesIndex: i,
            text: i === 0 ? ["+ chaud", "+ froid"] : ["", ""],
            formatter: (val: number) => `${val >= 0 ? "+" : ""}${val} °C`,
        })),
        grid: grids,
        xAxis: xAxes,
        yAxis: yAxes,
        series,
    } as unknown as object;
}
