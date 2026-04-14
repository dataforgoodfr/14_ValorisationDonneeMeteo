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

function periodKey(date: string, granularity: GranularityType): string {
    const length =
        granularity === "year" ? 4 : granularity === "month" ? 7 : 10;
    return date.substring(0, length);
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
