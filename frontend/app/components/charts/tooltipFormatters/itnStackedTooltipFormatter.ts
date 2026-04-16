import type { TooltipComponentFormatterCallbackParams } from "echarts";
import type { GranularityType } from "~/components/ui/commons/selectBar/types";

export function itnStackedTooltipFormatter(
    params: TooltipComponentFormatterCallbackParams,
    granularity: GranularityType,
): string {
    if (!Array.isArray(params) || params.length === 0) return "";
    const pos = params[0]!.axisValue as string;

    const header =
        granularity === "month"
            ? new Date(2000, parseInt(pos, 10) - 1, 1)
                  .toLocaleDateString("fr-FR", { month: "long" })
                  .replace(/^\w/, (c) => c.toUpperCase())
            : (() => {
                  const [mm, dd] = pos.split("-");
                  return new Date(
                      2000,
                      parseInt(mm!, 10) - 1,
                      parseInt(dd!, 10),
                  ).toLocaleDateString("fr-FR", {
                      day: "numeric",
                      month: "long",
                  });
              })();

    const fmt = (v: number) => `${v.toFixed(1)}°C`;
    const lines: string[] = [`<strong>${header}</strong>`];

    // Baseline stats are in the "Indicateur MF" dataset-encoded series
    const mfParam = params.find((p) => p.seriesName === "Indicateur MF");
    if (mfParam) {
        const row = mfParam.value as Record<string, number>;
        if (row.baseline_mean !== undefined)
            lines.push(
                `${mfParam.marker ?? ""}Indicateur MF : ${fmt(row.baseline_mean)}`,
            );
        if (row.baseline_min !== undefined && row.baseline_band !== undefined)
            lines.push(
                `Extrêmes : [${fmt(row.baseline_min)} – ${fmt(row.baseline_min + row.baseline_band)}]`,
            );
        if (
            row.baseline_std_dev_lower !== undefined &&
            row.baseline_std_dev_band !== undefined
        )
            lines.push(
                `Écart-type : [${fmt(row.baseline_std_dev_lower)} – ${fmt(row.baseline_std_dev_lower + row.baseline_std_dev_band)}]`,
            );
    }

    // One entry per selected year (inline data: [position, temperature])
    for (const p of params) {
        if (
            !p.seriesName ||
            ["Extrêmes", "Écart-type", "Indicateur MF"].includes(p.seriesName)
        )
            continue;
        const val = Array.isArray(p.value) ? p.value[1] : null;
        if (val !== null && val !== undefined)
            lines.push(
                `${p.marker ?? ""}${p.seriesName} : ${fmt(val as number)}`,
            );
    }

    return lines.join("<br/>");
}
