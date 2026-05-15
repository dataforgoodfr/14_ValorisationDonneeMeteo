import { interpolateMapColor } from "~/constants/colors";

export function formatDeviationMapTooltip(
    stationName: string,
    deviation: number,
    stops: [number, string][],
): string {
    const sign = deviation >= 0 ? "+" : "";
    const color = interpolateMapColor(deviation, stops);
    return `
        <div style="font-family:sans-serif;font-size:12px;line-height:1.5;padding:2px 4px">
            <div style="font-weight:600;margin-bottom:2px">${stationName}</div>
            <div style="color:${color}">${sign}${deviation.toFixed(1)} °C</div>
        </div>
    `;
}
