import type { TooltipComponentFormatterCallbackParams } from "echarts";
import { TEMPERATURE_COLORS } from "~/constants/colors";

export function recordsPyramidTooltipFormatter(
    params: TooltipComponentFormatterCallbackParams,
): string {
    if (!Array.isArray(params)) return "";

    const param = params[0];
    if (!param) return "";

    const label = String(param?.axisValue ?? "");
    const row = param.value as {
        period: string;
        hot: number;
        cold: number;
    };

    return (
        `<b>${label}</b><br/>` +
        `<span style="color:${TEMPERATURE_COLORS.hot}">● Records de chaleur : ${row.hot}</span><br/>` +
        `<span style="color:${TEMPERATURE_COLORS.cold}">● Records de froid : ${row.cold}</span><br/>` +
        `<span style="color:#aaa">Total : ${row.hot + row.cold}</span>`
    );
}
