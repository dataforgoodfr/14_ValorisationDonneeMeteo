import { deviationCalendarTooltipFormatter } from "~/components/charts/tooltipFormatters/deviationCalendarTooltipFormatter";
import type {
    EChartsOption,
    SeriesOption,
    TooltipComponentFormatterCallbackParams,
} from "echarts";
import type {
    ContinousVisualMapOption,
    GridOption,
    TitleOption,
    XAXisOption,
    YAXisOption,
} from "echarts/types/dist/shared";
import type {
    TemperatureDeviationGraphDataPoint,
    TemperatureDeviationGraphResponse,
    TemperatureDeviationGraphStationSerie,
} from "~/types/api";
import type { GranularityType } from "~/components/ui/commons/selectBar/types";
import type { DeviationStationIdAndName } from "~/types/common";
import { MONTH_SHORT } from "~/constants/months";
import { FONT_CHARTS } from "~/constants/fonts";
import { useMapColors } from "~/constants/colors";

// transforme "Jan-2024" en nombre comparable
function toMonthNumber(monthLabel: string): number {
    const [monthShortName, year] = monthLabel.split("-");

    if (!monthShortName || !year) {
        throw new Error(`Invalid month label: ${monthLabel}`);
    }

    const monthIndex = MONTH_SHORT.indexOf(monthShortName);
    const fullYear = parseInt(year, 10);

    return fullYear * 12 + monthIndex;
}

function buildCategoriesForYear(allDates: string[]): {
    xCategories: string[];
    yCategories: string[];
} {
    const years = [...new Set(allDates.map((d) => d.slice(0, 4)))].sort();

    return {
        xCategories: years,
        yCategories: MONTH_SHORT,
    };
}

function buildCategoriesForMonth(allDates: string[]): {
    xCategories: string[];
    yCategories: string[];
} {
    const monthLabels = [
        ...new Set(
            allDates.map((isoDate) => {
                const [year, month] = isoDate.split("-");

                if (!month) {
                    throw new Error(`Invalid month value: ${month}`);
                }
                const monthIndex = parseInt(month, 10) - 1;

                return `${MONTH_SHORT[monthIndex]}-${year}`;
            }),
        ),
    ].sort((monthLabelA, monthLabelB) => {
        const totalMonthsA = toMonthNumber(monthLabelA);
        const totalMonthsB = toMonthNumber(monthLabelB);

        return totalMonthsA - totalMonthsB;
    });

    return {
        xCategories: monthLabels,
        yCategories: Array.from({ length: 31 }, (_, i) => String(i + 1)),
    };
}

function buildCategories(
    data: TemperatureDeviationGraphResponse,
    granularity: GranularityType,
): { xCategories: string[]; yCategories: string[] } {
    const allDates = [
        ...(data.national?.data?.map(
            (d: TemperatureDeviationGraphDataPoint) => d.date,
        ) ?? []),
        ...data.stations.flatMap(
            (s: TemperatureDeviationGraphStationSerie) =>
                s.data?.map(
                    (d: TemperatureDeviationGraphDataPoint) => d.date,
                ) ?? [],
        ),
    ];

    if (granularity === "year") {
        return buildCategoriesForYear(allDates);
    }

    return buildCategoriesForMonth(allDates);
}

function splitIsoDate(isoDate: string): [string, string, string] {
    const parts = isoDate.split("-");

    if (parts.length !== 3) {
        throw new Error(`Invalid ISO date: ${isoDate}`);
    }

    return parts as [string, string, string];
}

function getMonthIndex(month: string): number {
    return parseInt(month, 10) - 1;
}

function buildMonthLabel(year: string, monthIndex: number): string {
    return `${MONTH_SHORT[monthIndex]}-${year}`;
}

function dateToXYYearMode(
    year: string,
    month: string,
    xCategories: string[],
): [number, number] | null {
    const monthIndex = getMonthIndex(month);

    const xIndex = xCategories.indexOf(year);
    const yIndex = monthIndex;

    return xIndex === -1 ? null : [xIndex, yIndex];
}

function dateToXYMonthMode(
    year: string,
    month: string,
    day: string,
    xCategories: string[],
): [number, number] | null {
    const monthIndex = getMonthIndex(month);

    const xLabel = buildMonthLabel(year, monthIndex);
    const xIndex = xCategories.indexOf(xLabel);
    const yIndex = parseInt(day, 10) - 1;

    return xIndex === -1 ? null : [xIndex, yIndex];
}

function dateToXY(
    isoDate: string,
    granularity: GranularityType,
    xCategories: string[],
): [number, number] | null {
    const [year, month, day] = splitIsoDate(isoDate);

    if (granularity === "year") {
        return dateToXYYearMode(year, month, xCategories);
    }

    return dateToXYMonthMode(year, month, day, xCategories);
}

export function useDeviationCalendarOption(
    data: TemperatureDeviationGraphResponse,
    granularity: GranularityType,
    stationsIdAndNames: DeviationStationIdAndName[],
): EChartsOption {
    const deviationStore = useDeviationStore();
    const mapColors = useMapColors();

    const stationsAndNational: TemperatureDeviationGraphStationSerie[] =
        deviationStore.stationsAndNationalFormatted(data);

    const stationCount = stationsAndNational.length || 1;
    const { xCategories, yCategories } = buildCategories(data, granularity);

    const totalHeightPct = 92;
    const gapBetweenPct = stationCount === 1 ? 0 : 15;
    const blockHeightPct =
        (totalHeightPct - (stationCount - 1) * gapBetweenPct) / stationCount;
    const topOffsetPct = 3;

    const grids: GridOption[] = [];
    const xAxes: XAXisOption[] = [];
    const yAxes: YAXisOption[] = [];
    const series: SeriesOption[] = [];
    const titles: TitleOption[] = [];

    // Cible ~12 labels max pour éviter le chevauchement sur les longues périodes
    const maxLabels = granularity === "year" ? 15 : 12;
    const labelInterval = Math.max(
        0,
        Math.ceil(xCategories.length / maxLabels) - 1,
    );
    const labelRotate = granularity === "year" ? 0 : 45;
    const xAxisName = granularity === "year" ? "Année" : "Mois";
    const yAxisName = granularity === "year" ? "Mois" : "Jour";

    stationsAndNational.forEach((stationOrNational, index) => {
        const top = topOffsetPct + index * (blockHeightPct + gapBetweenPct);
        const bottom = 100 - top - blockHeightPct;

        const stationName = getStationById(
            stationsIdAndNames,
            stationOrNational.station_id,
        )?.station_name;

        const heatmapData = (stationOrNational?.data ?? [])
            .map((point: TemperatureDeviationGraphDataPoint) => {
                const coordinates = dateToXY(
                    point.date,
                    granularity,
                    xCategories,
                );
                if (!coordinates) return null;

                return [...coordinates, point.deviation];
            })
            .filter((coords): coords is number[] => coords !== null);

        grids.push({
            top: `${top}%`,
            bottom: `${bottom}%`,
            left: "7%",
            right: "12%",
        });

        xAxes.push({
            type: "category",
            gridIndex: index,
            data: xCategories,
            splitArea: { show: true },
            axisTick: { show: false },
            axisLine: { lineStyle: { color: "#3a5080" } },
            axisLabel: {
                color: "#000000",
                fontSize: FONT_CHARTS.fontSize,
                interval: labelInterval,
                rotate: labelRotate,
            },
            name: index === stationCount - 1 ? xAxisName : "",
            nameLocation: "middle",
            nameGap: granularity === "year" ? 25 : 38,
            nameTextStyle: {
                color: mapColors.value.foreground,
                fontSize: FONT_CHARTS.fontSize,
                fontWeight: "bold",
            },
        });

        yAxes.push({
            type: "category",
            gridIndex: index,
            data: yCategories,
            splitArea: { show: true },
            axisTick: { show: false },
            axisLine: { lineStyle: { color: "#3a5080" } },
            axisLabel: {
                color: mapColors.value.foreground,
                fontSize: FONT_CHARTS.fontSize,
            },
            name: yAxisName,
            nameLocation: "middle",
            nameGap: 35,
            nameTextStyle: {
                color: mapColors.value.foreground,
                fontSize: FONT_CHARTS.fontSize,
                fontWeight: "bold",
            },
        });

        titles.push({
            text: stationName,
            top: `${top - 4}%`,
            right: "12%",
            textStyle: {
                fontSize: FONT_CHARTS.fontSize,
                fontWeight: "bold",
                color: mapColors.value.foreground,
            },
        });

        series.push({
            name: stationName,
            type: "heatmap",
            xAxisIndex: index,
            yAxisIndex: index,
            data: heatmapData,
            label: { show: false },
            emphasis: {
                itemStyle: {
                    shadowBlur: 10,
                    shadowColor: "rgba(0,0,0,0.5)",
                },
            },
        });
    });

    const visualMap: ContinousVisualMapOption = {
        min: -5,
        max: +5,
        calculable: true,
        show: true,
        orient: "vertical",
        right: "0%",
        bottom: "center",
        inRange: {
            color: [mapColors.value.cold, "#FFF", mapColors.value.hot],
        },
        textStyle: { color: mapColors.value.foreground },
        handleStyle: { borderColor: "#3a5080" },
        seriesIndex: series.map((_, i) => i),
        text: ["+ chaud", "+ froid"],
        formatter: (val: unknown): string => {
            if (typeof val !== "number" && typeof val !== "string") {
                return "";
            }

            const num = Number(val);

            return `${num >= 0 ? "+" : ""}${num} °C`;
        },
    };

    return {
        title: titles,
        tooltip: {
            formatter: (params: TooltipComponentFormatterCallbackParams) =>
                deviationCalendarTooltipFormatter(params, granularity, {
                    xAxis: xCategories,
                    yAxis: yCategories,
                }),
        },
        visualMap,
        grid: grids,
        xAxis: xAxes,
        yAxis: yAxes,
        series,
    };
}
