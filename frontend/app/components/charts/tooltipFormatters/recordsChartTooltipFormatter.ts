import type {
    DefaultLabelFormatterCallbackParams,
    TooltipComponentFormatterCallbackParams,
} from "echarts";
import type { GranularityType } from "~/components/ui/commons/selectBar/types";

function formatBarTooltip(param: DefaultLabelFormatterCallbackParams): string {
    const data = param.value as Record<string, number | string>;
    const hotMarker = `<span style="display:inline-block;margin-right:4px;border-radius:10px;width:10px;height:10px;background-color:#d32f2f;"></span>`;
    const coldMarker = `<span style="display:inline-block;margin-right:4px;border-radius:10px;width:10px;height:10px;background-color:#1976d2;"></span>`;
    return [
        `<b>${data.period}</b>`,
        `${hotMarker} Records de chaleur : ${data.hot}`,
        `${coldMarker} Records de froid : ${data.cold}`,
    ].join("<br/>");
}

function formatScatterTooltip(
    paramsArray: DefaultLabelFormatterCallbackParams[],
    granularity: GranularityType,
): string {
    const firstParam = paramsArray[0] as DefaultLabelFormatterCallbackParams;
    const scatterData = firstParam.value as Record<string, number | string>;

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
        scatterData.date as string,
    ).toLocaleDateString("fr-FR", dateOptions);

    const tooltipLabelFormatter = (
        serie: DefaultLabelFormatterCallbackParams,
    ) => {
        const data = serie.value as Record<string, number | string | null>;
        if (data?.value === null) return [];

        return [`${serie?.marker ?? ""} ${data?.station} : ${data?.value}°C`];
    };

    const tooltipContent = paramsArray
        .flatMap(tooltipLabelFormatter)
        .join("<br/>");

    return [formattedDate, tooltipContent].join("<br/>");
}

export function recordsChartTooltipFormatter(
    params: TooltipComponentFormatterCallbackParams,
    granularity: GranularityType,
): string {
    const paramsArray = Array.isArray(params) ? params : [params];
    if (paramsArray.length === 0) return "";

    const firstParam = paramsArray[0] as DefaultLabelFormatterCallbackParams;

    if (firstParam.seriesType === "bar") {
        return formatBarTooltip(firstParam);
    }

    return formatScatterTooltip(paramsArray, granularity);
}
