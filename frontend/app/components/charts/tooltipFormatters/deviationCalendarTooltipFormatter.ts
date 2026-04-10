import type { TooltipComponentFormatterCallbackParams } from "echarts";
import type { GranularityType } from "~/components/ui/commons/selectBar/types";

const COLOR_POS = "#d32f2f";
const COLOR_NEG = "#1976d2";

export function deviationCalendarTooltipFormatter(
    params: TooltipComponentFormatterCallbackParams,
    granularity: GranularityType,
    stationsNames: string[],
): string {
    if (!Array.isArray(params) || !params.length) return "";
    const p = params[0];
    if (!p || !Array.isArray(p.data) || p.data[2] == null) return "";

    // (x,y) = (année,mois) ou (mois,jour) selon granularité choisie
    const xIdx = p.data[0] as number;
    const yIdx = p.data[1] as number;
    const val = p.data[2] as number;

    // Reconstitue la date depuis les index d'axes
    const xLabel = String(xIdx);
    const yLabel = String(yIdx);
    const dateStr =
        granularity === "year"
            ? `${xLabel} · ${yLabel}`
            : `${yLabel}/${xLabel}`;

    const col = val >= 0 ? COLOR_POS : COLOR_NEG;
    const plusSign = val >= 0 ? "+" : "";
    const station = stationsNames[p.seriesIndex ?? 0] ?? "";

    return (
        `<b style="color:#fff">${station}</b><br/>` +
        `<span style="color:#aaa">${dateStr}</span><br/>` +
        `<span style="color:${col}">● ${plusSign}${val.toFixed(1)} °C</span>`
    );
}
