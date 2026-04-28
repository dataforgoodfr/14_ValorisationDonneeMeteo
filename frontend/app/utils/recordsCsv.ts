import type { TemperatureRecordFlatEntry } from "~/types/api";
import { escapeCsvValue } from "./string";

const HEADERS = [
    "Station",
    "Département",
    "Record (°C)",
    "Date du record",
].join(",");

export function buildRecordsCsv(records: TemperatureRecordFlatEntry[]): string {
    const rows = records
        .map((s) =>
            [
                escapeCsvValue(s.station_name),
                escapeCsvValue(s.department),
                s.record_value,
                s.record_date,
            ].join(","),
        )
        .join("\n");
    return `${HEADERS}\n${rows}`;
}
