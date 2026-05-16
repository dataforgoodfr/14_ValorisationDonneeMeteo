import { getMapColor } from "~/constants/colors";

export function formatDeviationMapTooltip(
    stationName: string,
    deviation: number,
    stops: [number, string][],
): string {
    const sign = deviation >= 0 ? "+" : "";
    const color = getMapColor(deviation, stops);
    return `
        <div style="font-family:sans-serif;font-size:12px;line-height:1.5;padding:2px 8px 2px 10px;border-left:3px solid ${color}">
            <div style="font-weight:600;margin-bottom:2px">${stationName}</div>
            <div>${sign}${deviation.toFixed(1)} °C</div>
        </div>
    `;
}
