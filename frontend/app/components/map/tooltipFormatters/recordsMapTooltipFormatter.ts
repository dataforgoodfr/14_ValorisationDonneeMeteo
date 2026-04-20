import { COLORS } from "~/constants/colors";

export function formatRecordsMapTooltip(
    stationName: string,
    value: number,
    recordDate: string | null,
): string {
    const sign = value >= 0 ? "+" : "";
    const color = value >= 0 ? COLORS.positive : COLORS.negative;
    const formattedDate = recordDate
        ? new Date(recordDate).toLocaleDateString("fr-FR")
        : null;
    return `
        <div style="font-family:sans-serif;font-size:12px;line-height:1.5;padding:2px 4px">
            <div style="font-weight:600;margin-bottom:2px">${stationName}</div>
            <div style="color:${color}">${sign}${value.toFixed(1)} °C</div>
            ${formattedDate ? `<div style="color:#666">${formattedDate}</div>` : ""}
        </div>
    `;
}
