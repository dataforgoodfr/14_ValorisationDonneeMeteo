import type { TooltipComponentFormatterCallbackParams } from "echarts";
import type { GranularityType } from "~/components/ui/commons/selectBar/types";

export function deviationChartTooltipFormatter(
    params: TooltipComponentFormatterCallbackParams,
    granularity: GranularityType,
): string {
    if (!Array.isArray(params)) return "";
    const [first] = params;
    if (!first) return "";

    const d = first.value as Record<string, number | string>;
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

    const deviation = (d.deviation_positive ?? d.deviation_negative) as number;
    const serie =
        deviation >= 0 ? find("Ecart positif") : find("Ecart négatif");
    const sign = deviation >= 0 ? "+" : "";

    return [
        formattedDate,
        `${serie?.marker ?? ""} : ${sign}${fmt(deviation)}`,
    ].join("<br/>");
}
