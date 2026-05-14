import type { TemperatureRecordFlatEntry } from "~/types/api";
import { escapeCsvValue } from "./string";

export function buildRecordsCsv(
    records: TemperatureRecordFlatEntry[],
    valueLabel = "Record absolu (°C)",
): string {
    const headers = [
        "Station",
        "Département",
        valueLabel,
        "Date du record",
        "Classe",
        "Altitude (m)",
        "Année de création",
    ].join(",");
    const rows = records
        .map((s) =>
            [
                escapeCsvValue(s.station_name),
                escapeCsvValue(s.department),
                s.record_value,
                s.record_date,
                s.classe_recente,
                s.alt,
                new Date(s.date_de_creation).getFullYear(),
            ].join(","),
        )
        .join("\n");
    return `${headers}\n${rows}`;
}
