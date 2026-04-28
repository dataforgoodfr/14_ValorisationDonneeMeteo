import { TEMPERATURE_COLORS } from "~/constants/colors";

export function formatDeviationMapTooltip(
    stationName: string,
    deviation: number,
): string {
    const sign = deviation >= 0 ? "+" : "";
    const color =
        deviation >= 0 ? TEMPERATURE_COLORS.hot : TEMPERATURE_COLORS.cold;
    return `
        <div style="font-family:sans-serif;font-size:12px;line-height:1.5;padding:2px 4px">
            <div style="font-weight:600;margin-bottom:2px">${stationName}</div>
            <div style="color:${color}">${sign}${deviation.toFixed(1)} °C</div>
        </div>
    `;
}
