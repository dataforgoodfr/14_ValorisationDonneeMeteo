import type { TemperatureRecordsResponse } from "~/types/api";
import type { GranularityType } from "~/components/ui/commons/selectBar/types";

interface RecordEntry {
    date: string;
    value: number;
    station: string;
}

export function flattenHotRecords(
    data: TemperatureRecordsResponse,
): RecordEntry[] {
    return data.stations.flatMap((station) =>
        station.hot_records.map((record) => ({
            date: record.date,
            value: record.value,
            station: station.name,
        })),
    );
}

export function flattenColdRecords(
    data: TemperatureRecordsResponse,
): RecordEntry[] {
    return data.stations.flatMap((station) =>
        station.cold_records.map((record) => ({
            date: record.date,
            value: record.value,
            station: station.name,
        })),
    );
}

export function periodKey(date: string, granularity: GranularityType): string {
    const length =
        granularity === "year"
            ? "YYYY".length
            : granularity === "month"
              ? "YYYY-MM".length
              : "YYYY-MM-DD".length;
    return date.substring(0, length);
}

// Arrondit au multiple supérieur d'un pas "rond" pour que le dernier tick
// respecte l'espacement régulier (évite un tick isolé en bout d'axe).
export function niceMax(value: number): number {
    const steps = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000];
    const roughStep = Math.max(value, 1) / 5; // cible ~5 ticks
    const step = steps.find((s) => s >= roughStep) ?? 1000;
    return Math.ceil(value / step) * step;
}

export function countByPeriod(
    records: { date: string }[],
    granularity: GranularityType,
): Record<string, number> {
    return records.reduce(
        (acc, record) => {
            const period = periodKey(record.date, granularity);
            acc[period] = (acc[period] ?? 0) + 1;
            return acc;
        },
        {} as Record<string, number>,
    );
}
