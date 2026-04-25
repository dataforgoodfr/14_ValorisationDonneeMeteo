import type { TooltipComponentFormatterCallbackParams } from "echarts";
import type { GranularityType } from "~/components/ui/commons/selectBar/types";
import { ITN_SERIES } from "~/constants/itn";

export function itnChartTooltipFormatter(
    params: TooltipComponentFormatterCallbackParams,
    granularity: GranularityType,
): string {
    if (!Array.isArray(params)) return "";
    const [first] = params;
    if (!first) return "";

    const d = first.value as Record<string, number | string>;
    if (d.isInterpolated) return "";
    const fmt = (v: number) => `${v.toFixed(1)}°C`;
    const find = (name: string) => params.find((p) => p.seriesName === name);

    const dateOptions: Intl.DateTimeFormatOptions =
        granularity === "month"
            ? { year: "numeric", month: "long" }
            : granularity === "year"
              ? { year: "numeric" }
              : {
                    weekday: "short",
                    day: "numeric",
                    month: "short",
                    year: "numeric",
                };
    const formattedDate = new Date(d.date as string).toLocaleDateString(
        "fr-FR",
        dateOptions,
    );

    return [
        formattedDate,
        `${find(ITN_SERIES.temperature)?.marker ?? ""}${ITN_SERIES.temperature} : ${fmt(d.temperature as number)}`,
        `${find(ITN_SERIES.baseline)?.marker ?? ""}${ITN_SERIES.baseline} : ${fmt(d.baseline_mean as number)}`,
        `${find(ITN_SERIES.extremes)?.marker ?? ""}${ITN_SERIES.extremes} : [${fmt(d.baseline_min as number)} – ${fmt(d.baseline_max as number)}]`,
        `${find(ITN_SERIES.stdDev)?.marker ?? ""}${ITN_SERIES.stdDev} : [${fmt(d.baseline_std_dev_lower as number)} – ${fmt(d.baseline_std_dev_upper as number)}]`,
    ].join("<br/>");
}
