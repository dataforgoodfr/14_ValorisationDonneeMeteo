import type { TemperatureDeviationStation } from "~/types/api";
import { escapeCsvValue } from "./string";

const HEADERS = [
    "Station",
    "Département",
    "Région",
    "Écart à la normale (°C)",
    "Température Moyenne (°C)",
].join(",");

export function buildDeviationCsv(
    stations: TemperatureDeviationStation[],
): string {
    const rows = stations
        .map((s) =>
            [
                escapeCsvValue(s.station_name),
                escapeCsvValue(s.department),
                escapeCsvValue(s.region),
                s.deviation?.toFixed(1) ?? "",
                s.temperature_mean?.toFixed(1) ?? "",
            ].join(","),
        )
        .join("\n");
    return `${HEADERS}\n${rows}`;
}
