import type { TooltipComponentFormatterCallbackParams } from "echarts";

const COLOR_HOT = "#d32f2f";
const COLOR_COLD = "#1976d2";

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
        `<span style="color:${COLOR_HOT}">● Records de chaleur : ${row.hot}</span><br/>` +
        `<span style="color:${COLOR_COLD}">● Records de froid : ${row.cold}</span><br/>` +
        `<span style="color:#aaa">Total : ${row.hot + row.cold}</span>`
    );
}
