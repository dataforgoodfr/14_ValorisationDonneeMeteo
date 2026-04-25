import { getStationById } from "~/utils/station";
import type {
    DefaultLabelFormatterCallbackParams,
    TooltipComponentFormatterCallbackParams,
} from "echarts";
import type { GranularityType } from "~/components/ui/commons/selectBar/types";
import type { DeviationStationIdAndName } from "~/types/common";

interface DeviationChartTooltipParam {
    date: string;
    deviation_negative: number | null;
    deviation_positive: number | null;
    station_id: string;
}

export function deviationChartTooltipFormatter(
    params: TooltipComponentFormatterCallbackParams,
    granularity: GranularityType,
    stationsIdAndNames: DeviationStationIdAndName[],
): string {
    if (!Array.isArray(params) || params.length === 0) return "";

    const firstParam = params[0]?.value as DeviationChartTooltipParam;

    const dateOptions: Intl.DateTimeFormatOptions = (() => {
        if (granularity === "month") {
            return { year: "numeric", month: "long" };
        }
        if (granularity === "year") {
            return { year: "numeric" };
        }
        return {
            weekday: "short",
            day: "numeric",
            month: "short",
            year: "numeric",
        };
    })();

    const formattedDate = new Date(
        firstParam.date as string,
    ).toLocaleDateString("fr-FR", dateOptions);

    const tooltipLabelFormatter = (
        serie: DefaultLabelFormatterCallbackParams,
    ) => {
        const data = serie.data as DeviationChartTooltipParam;

        if (
            serie.seriesName === "Écart positif" &&
            data?.deviation_positive === null
        )
            return [];
        if (
            serie.seriesName === "Écart négatif" &&
            data?.deviation_negative === null
        )
            return [];

        const stationName =
            serie.axisIndex !== undefined
                ? (getStationById(stationsIdAndNames, data?.station_id)
                      ?.station_name ?? "")
                : "";

        const deviation =
            data?.deviation_positive || data?.deviation_negative || 0;

        const plusSign = Math.sign(deviation) === 1 ? "+" : "";

        return [
            `${serie?.marker ?? ""} ${stationName} : ${plusSign}${deviation.toFixed(1)}°C`,
        ];
    };

    const tooltipContent = () =>
        params.flatMap(tooltipLabelFormatter).join("<br/>");

    return [formattedDate, tooltipContent()].join("<br/>");
}
