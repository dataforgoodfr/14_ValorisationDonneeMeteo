import type { TemperatureRecordsGraphResponse } from "~/types/api";
import type { GranularityType } from "~/components/ui/commons/selectBar/types";
import type { BarSeriesOption, ScatterSeriesOption } from "echarts/charts";

export function scatterSeries(
    opts: Partial<ScatterSeriesOption>,
): ScatterSeriesOption {
    return { type: "scatter", ...opts };
}

export function barSeries(opts: Partial<BarSeriesOption>): BarSeriesOption {
    return { type: "bar", ...opts };
}

export interface RecordEntry {
    date: string;
    value: number;
    station: string;
}

export function flattenHotRecords(
    data: TemperatureRecordsGraphResponse,
): RecordEntry[] {
    return data.records
        .filter((r) => r.type_records === "hot")
        .map((r) => ({
            date: r.date,
            value: r.valeur,
            station: r.station_name,
        }));
}

export function flattenColdRecords(
    data: TemperatureRecordsGraphResponse,
): RecordEntry[] {
    return data.records
        .filter((r) => r.type_records === "cold")
        .map((r) => ({
            date: r.date,
            value: r.valeur,
            station: r.station_name,
        }));
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

function recordsForTerritory(
    territory: { type: string; id: string },
    data: TemperatureRecordsGraphResponse,
): { hot: RecordEntry[]; cold: RecordEntry[] } {
    if (territory.type !== "STATION") {
        return { hot: flattenHotRecords(data), cold: flattenColdRecords(data) };
    }
    return {
        hot: data.records
            .filter(
                (r) =>
                    r.type_records === "hot" && r.station_id === territory.id,
            )
            .map((r) => ({
                date: r.date,
                value: r.valeur,
                station: r.station_name,
            })),
        cold: data.records
            .filter(
                (r) =>
                    r.type_records === "cold" && r.station_id === territory.id,
            )
            .map((r) => ({
                date: r.date,
                value: r.valeur,
                station: r.station_name,
            })),
    };
}

export function buildTerritoryPlots(
    selectedTerritories: Array<{ type: string; id: string; value: string }>,
    data: TemperatureRecordsGraphResponse,
): { name: string; hot: RecordEntry[]; cold: RecordEntry[] }[] {
    if (selectedTerritories.length === 0) {
        return [
            {
                name: "France Métropolitaine",
                hot: flattenHotRecords(data),
                cold: flattenColdRecords(data),
            },
        ];
    }
    return selectedTerritories.map((t) => ({
        name: t.value,
        ...recordsForTerritory(t, data),
    }));
}
