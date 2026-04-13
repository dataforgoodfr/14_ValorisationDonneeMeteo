import type { TooltipComponentFormatterCallbackParams } from "echarts";

const COLOR_HOT = "#d32f2f";
const COLOR_COLD = "#1976d2";

export function recordsPyramidTooltipFormatter(
    params: TooltipComponentFormatterCallbackParams,
): string {
    if (!Array.isArray(params) || !params.length) return "";

    const label = String(params[0]?.axisValue ?? "");
    let html = `<b style="color:#fff">${label}</b><br/>`;

    const seen: Record<string, { hot: number; cold: number }> = {};

    for (const p of params) {
        const parts = (p.seriesName ?? "").split(" · ");
        const type = parts[0];
        const station = parts[1];
        if (!station) continue;
        if (!seen[station]) seen[station] = { hot: 0, cold: 0 };
        if (type === "Chauds") seen[station].hot = (p.value as number) ?? 0;
        if (type === "Froids") seen[station].cold = (p.value as number) ?? 0;
    }

    for (const [station, v] of Object.entries(seen)) {
        html += `<span style="color:#aaa">${station}</span><br/>`;
        html += `<span style="color:${COLOR_HOT}">● Chauds : ${v.hot}</span>&nbsp;&nbsp;`;
        html += `<span style="color:${COLOR_COLD}">● Froids : ${v.cold}</span>&nbsp;&nbsp;`;
        html += `<span style="color:#aaa">Total : ${v.hot + v.cold}</span><br/>`;
    }

    return html;
}
