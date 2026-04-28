import type {
    DefaultLabelFormatterCallbackParams,
    TooltipComponentFormatterCallbackParams,
} from "echarts";
import type { GranularityType } from "~/components/ui/commons/selectBar/types";
import { TEMPERATURE_COLORS } from "~/constants/colors";

function formatBarTooltip(param: DefaultLabelFormatterCallbackParams): string {
    const data = param.value as Record<string, number | string>;
    const hotMarker = `<span style="display:inline-block;margin-right:4px;border-radius:10px;width:10px;height:10px;background-color:${TEMPERATURE_COLORS.cold};"></span>`;
    const coldMarker = `<span style="display:inline-block;margin-right:4px;border-radius:10px;width:10px;height:10px;background-color:${TEMPERATURE_COLORS.hot};"></span>`;
    return [
        `<b>${data.period}</b>`,
        `${hotMarker} Records de chaleur : ${data.hot}`,
        `${coldMarker} Records de froid : ${data.cold}`,
    ].join("<br/>");
}

function formatScatterTooltip(
    paramsArray: DefaultLabelFormatterCallbackParams[],
    _granularity: GranularityType,
): string {
    const firstParam = paramsArray[0] as DefaultLabelFormatterCallbackParams;
    const scatterData = firstParam.value as Record<string, number | string>;

    const formattedDate = new Date(
        scatterData.date as string,
    ).toLocaleDateString("fr-FR", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
    });

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
