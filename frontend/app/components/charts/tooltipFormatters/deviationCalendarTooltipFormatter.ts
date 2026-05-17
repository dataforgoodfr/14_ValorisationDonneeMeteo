import type { TooltipComponentFormatterCallbackParams } from "echarts";
import type { GranularityType } from "~/components/ui/commons/selectBar/types";
import { TEMPERATURE_COLORS } from "~/constants/colors";

export function deviationCalendarTooltipFormatter(
    params: TooltipComponentFormatterCallbackParams,
    granularity: GranularityType,
    categories: Record<"xAxis" | "yAxis", string[]>,
    vertical = false,
): string {
    if (vertical) {
        // trigger "axis" → params est un tableau ; on garde un item par série
        const paramsArray = Array.isArray(params) ? params : [params];
        const seen = new Set<number>();
        const unique = paramsArray.filter((p) => {
            const idx = p.seriesIndex ?? -1;
            if (seen.has(idx)) return false;
            seen.add(idx);
            return true;
        });

        const first = unique[0];
        if (!first || !Array.isArray(first.data)) return "";

        const [xIndex] = first.data as [number, number, number];
        const xLabel = categories.xAxis[xIndex] ?? String(xIndex);

        return unique
            .map((p) => {
                if (!Array.isArray(p.data)) return "";
                const [, , val] = p.data as [number, number, number];
                const col =
                    val >= 0 ? TEMPERATURE_COLORS.hot : TEMPERATURE_COLORS.cold;
                const plusSign = val >= 0 ? "+" : "";
                return (
                    `<b style="color:#000">${p.seriesName}</b><br/>` +
                    `<span style="color:#aaa">${xLabel}</span><br/>` +
                    `<span style="color:${col}">● ${plusSign}${val.toFixed(1)} °C</span>`
                );
            })
            .filter(Boolean)
            .join("<br/><br/>");
    }

    if (!("data" in params) || !Array.isArray(params.data)) {
        return "";
    }

    const data = params.data as [number, number, number];

    // (x,y) = (année,mois) ou (mois,jour) selon granularité choisie
    const [xIndex, yIndex, val] = data;

    // Reconstitue la date depuis les index d'axes
    const xLabel = categories.xAxis[xIndex] ?? String(xIndex);
    const yLabel = categories.yAxis[yIndex] ?? String(yIndex);
    const dateStr =
        granularity === "year"
            ? `${xLabel} · ${yLabel}`
            : `${yLabel}/${xLabel}`;

    const col = val >= 0 ? TEMPERATURE_COLORS.hot : TEMPERATURE_COLORS.cold;
    const plusSign = val >= 0 ? "+" : "";
    const station = params.seriesName;

    return (
        `<b style="color:#000">${station}</b><br/>` +
        `<span style="color:#aaa">${dateStr}</span><br/>` +
        `<span style="color:${col}">● ${plusSign}${val.toFixed(1)} °C</span>`
    );
}
