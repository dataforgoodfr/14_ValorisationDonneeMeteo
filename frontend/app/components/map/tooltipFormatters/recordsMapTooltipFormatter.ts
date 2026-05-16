import { getMapColor } from "~/constants/colors";

export function formatRecordsMapTooltip(
    stationName: string,
    value: number,
    recordDate: string | null,
    stops: [number, string][],
): string {
    const sign = value >= 0 ? "+" : "";
    const color = getMapColor(value, stops);
    const formattedDate = recordDate
        ? new Date(recordDate).toLocaleDateString("fr-FR")
        : null;
    return `
        <div style="font-family:sans-serif;font-size:12px;line-height:1.5;padding:2px 8px 2px 10px;border-left:3px solid ${color}">
            <div style="font-weight:600;margin-bottom:2px">${stationName}</div>
            <div>${sign}${value.toFixed(1)} °C</div>
            ${formattedDate ? `<div style="opacity:0.6">${formattedDate}</div>` : ""}
        </div>
    `;
}
