import type { TooltipComponentFormatterCallbackParams } from "echarts";
import type { GranularityType } from "~/components/ui/commons/selectBar/types";
import { MONTH_SHORT } from "~/constants/months";
import { XX } from "~/utils/string";
import { ITN_SERIES } from "~/constants/itn";

interface BaselineRow {
    baseline_mean?: number;
    baseline_min?: number;
    baseline_band?: number;
    baseline_std_dev_lower?: number;
    baseline_std_dev_band?: number;
}

function isBaselineRow(v: unknown): v is BaselineRow {
    return typeof v === "object" && v !== null && !Array.isArray(v);
}

interface TooltipParam {
    value: unknown;
    marker?: unknown;
}

function formatBaselineLines(
    param: TooltipParam,
    fmt: (v: number) => string,
): string[] {
    if (!isBaselineRow(param.value)) return [];
    const row = param.value;
    const lines: string[] = [];
    if (row.baseline_mean !== undefined)
        lines.push(
            `${String(param.marker ?? "")}${ITN_SERIES.baseline} : ${fmt(row.baseline_mean)}`,
        );
    if (row.baseline_min !== undefined && row.baseline_band !== undefined)
        lines.push(
            `${ITN_SERIES.extremes} : [${fmt(row.baseline_min)} – ${fmt(row.baseline_min + row.baseline_band)}]`,
        );
    if (
        row.baseline_std_dev_lower !== undefined &&
        row.baseline_std_dev_band !== undefined
    )
        lines.push(
            `${ITN_SERIES.stdDev} : [${fmt(row.baseline_std_dev_lower)} – ${fmt(row.baseline_std_dev_lower + row.baseline_std_dev_band)}]`,
        );
    return lines;
}

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

    const mfParam = params.find((p) => p.seriesName === ITN_SERIES.baseline);
    if (mfParam) lines.push(...formatBaselineLines(mfParam, fmt));

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
        const val = Array.isArray(p.value) ? p.value[1] : null;
        if (typeof val === "number")
            lines.push(
                `${String(p.marker ?? "")}${p.seriesName} : ${fmt(val)}`,
            );
    }

    return lines.join("<br/>");
}
