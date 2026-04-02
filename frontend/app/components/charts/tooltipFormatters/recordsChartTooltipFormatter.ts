import type {
    DefaultLabelFormatterCallbackParams,
    TooltipComponentFormatterCallbackParams,
} from "echarts";
import type { GranularityType } from "~/components/ui/commons/selectBar/types";

export function recordsChartTooltipFormatter(
    params: TooltipComponentFormatterCallbackParams,
    granularity: GranularityType,
): string {
    const paramsArray = Array.isArray(params) ? params : [params];
    if (paramsArray.length === 0) return "";

    const firstParam = paramsArray[0]?.value as Record<string, number | string>;

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
        const data = serie.value as Record<string, number | string | null>;
        if (data?.value === null) return [];

        return [
            `${serie?.marker ?? ""} ${data?.station} (${serie.seriesName}) : ${data?.value}°C`,
        ];
    };

    const tooltipContent = () =>
        paramsArray.flatMap(tooltipLabelFormatter).join("<br/>");

    return [formattedDate, tooltipContent()].join("<br/>");
}
