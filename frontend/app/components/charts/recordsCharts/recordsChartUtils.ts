import type { TemperatureRecordsResponse } from "~/types/api";
import type { GranularityType } from "~/components/ui/commons/selectBar/types";

export function flattenHotRecords(data: TemperatureRecordsResponse) {
    return data.stations.flatMap((station) =>
        station.hot_records.map((record) => ({
            date: record.date,
            value: record.value,
            station: station.name,
        })),
    );
}

export function flattenColdRecords(data: TemperatureRecordsResponse) {
    return data.stations.flatMap((station) =>
        station.cold_records.map((record) => ({
            date: record.date,
            value: record.value,
            station: station.name,
        })),
    );
}

export function countByPeriod(
    records: { date: string }[],
    granularity: GranularityType,
) {
    return records.reduce(
        (acc, record) => {
            const period = record.date.substring(
                0,
                granularity === "year" ? 4 : granularity === "month" ? 7 : 10,
            );
            acc[period] = (acc[period] ?? 0) + 1;
            return acc;
        },
        {} as Record<string, number>,
    );
}
