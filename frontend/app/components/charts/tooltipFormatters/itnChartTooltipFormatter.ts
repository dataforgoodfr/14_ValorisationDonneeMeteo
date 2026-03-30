import type { TooltipComponentFormatterCallbackParams } from "echarts";
import type { GranularityType } from "~/components/ui/commons/selectBar/types";

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
        `${find("Température")?.marker ?? ""}Température : ${fmt(d.temperature as number)}`,
        `${find("Indicateur MF")?.marker ?? ""}Indicateur MF : ${fmt(d.baseline_mean as number)}`,
        `${find("Extrêmes")?.marker ?? ""}Extrêmes : [${fmt(d.baseline_min as number)} – ${fmt(d.baseline_max as number)}]`,
        `${find("Écart-type")?.marker ?? ""}Écart-type : [${fmt(d.baseline_std_dev_lower as number)} – ${fmt(d.baseline_std_dev_upper as number)}]`,
    ].join("<br/>");
}
