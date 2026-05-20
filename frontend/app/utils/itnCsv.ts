import type { NationalIndicatorDataPoint } from "~/types/api";

export function buildItnCsv(
    itnResponse: NationalIndicatorDataPoint[],
    type: "hot" | "cold",
): string {
    const headers = ["Date", "ITN (°C)", "ITN_baseline_mean (°C)"].join(",");
    const rows = itnResponse
        .filter((itn) => {
            if (type === "hot") {
                return itn.temperature > itn.baseline_std_dev_upper;
            } else {
                return itn.temperature < itn.baseline_std_dev_lower;
            }
        })
        .map((filteredItn) =>
            [
                filteredItn.date,
                filteredItn.temperature,
                filteredItn.baseline_mean,
            ].join(","),
        )
        .join("\n");
    return `${headers}\n${rows}`;
}
