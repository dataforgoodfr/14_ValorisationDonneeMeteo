import type { TooltipComponentFormatterCallbackParams } from "echarts";
import { useMapColors } from "~/constants/colors";

const mapColors = useMapColors();
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
        `<span style="color:${mapColors.value.hot}">● Records de chaleur : ${row.hot}</span><br/>` +
        `<span style="color:${mapColors.value.cold}">● Records de froid : ${row.cold}</span><br/>` +
        `<span style="color:#aaa">Total : ${row.hot + row.cold}</span>`
    );
}
