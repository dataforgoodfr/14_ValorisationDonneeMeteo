import type { TooltipComponentFormatterCallbackParams } from "echarts";
import type { GranularityType } from "~/components/ui/commons/selectBar/types";
import { MONTH_SHORT } from "~/constants/months";
import { XX } from "~/utils/string";
import { ITN_SERIES } from "~/constants/itn";

export function formatContinuousAxisLabel(value: number): string {
    const date = new Date(value);
    return `${XX(date.getDate())}-${MONTH_SHORT[date.getMonth()]}`;
}

export function formatStackedAxisLabel(
    val: string,
    granularity: "month" | "day",
): string {
    if (granularity === "month") {
        return MONTH_SHORT[parseInt(val, 10) - 1] ?? val;
    }
    const [mm] = val.split("-");
    return `01-${MONTH_SHORT[parseInt(mm!, 10) - 1] ?? val}`;
}

export function formatStackedPosition(
    pos: string,
    granularity: "month" | "day",
): string {
    if (granularity === "month") {
        return new Date(2000, parseInt(pos, 10) - 1, 1)
            .toLocaleDateString("fr-FR", { month: "long" })
            .replace(/^\w/, (c) => c.toUpperCase());
    }
    const [mm, dd] = pos.split("-");
    return new Date(
        2000,
        parseInt(mm!, 10) - 1,
        parseInt(dd!, 10),
    ).toLocaleDateString("fr-FR", { day: "numeric", month: "long" });
}

export function itnStackedTooltipFormatter(
    params: TooltipComponentFormatterCallbackParams,
    granularity: GranularityType,
): string {
    if (!Array.isArray(params) || params.length === 0) return "";
    const pos = String(params[0]!.axisValue);

    const header = formatStackedPosition(
        pos,
        granularity === "year" ? "month" : granularity,
    );

    const fmt = (v: number) => `${v.toFixed(1)}°C`;
    const lines: string[] = [`<strong>${header}</strong>`];

    const baselineParam = params.find(
        (p) => p.seriesName === ITN_SERIES.baseline,
    );
    if (baselineParam) {
        const yDimIndex = baselineParam.encode?.["y"]?.[0] ?? 1;
        const val = Array.isArray(baselineParam.value)
            ? baselineParam.value[yDimIndex]
            : null;
        if (typeof val === "number")
            lines.push(
                `${String(baselineParam.marker ?? "")}${ITN_SERIES.baseline} : ${fmt(val)}`,
            );
    }

    // One entry per selected year (inline data: [position, temperature])
    for (const p of params) {
        if (
            !p.seriesName ||
            [
                ITN_SERIES.extremes,
                ITN_SERIES.stdDev,
                ITN_SERIES.baseline,
            ].includes(p.seriesName)
        )
            continue;
        const yDimIndex = p.encode?.["y"]?.[0] ?? 1;
        const val = Array.isArray(p.value) ? p.value[yDimIndex] : null;
        if (typeof val === "number")
            lines.push(
                `${String(p.marker ?? "")}${p.seriesName} : ${fmt(val)}`,
            );
    }

    return lines.join("<br/>");
}
