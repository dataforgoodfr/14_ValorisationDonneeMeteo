import type {
    TemperatureRecordFlatEntry,
    TemperatureRecordsGraphRecord,
} from "~/types/api";
import type { GranularityType } from "~/components/ui/commons/selectBar/types";
import type { RecordEntry } from "./recordsChartUtils";
import { countByPeriod } from "./recordsChartUtils";
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

export function getRecordKindLabels(kind: string): {
    kindLabel: string;
    kindFileLabel: string;
} {
    const isHistorical = kind === "historical";
    return {
        kindLabel: isHistorical ? "records battus" : "records absolus",
        kindFileLabel: isHistorical ? "battus" : "absolus",
    };
}

export function buildPyramidRecordsCsv(
    territoryPlots: { name: string; hot: RecordEntry[]; cold: RecordEntry[] }[],
    kindLabel: string,
    granularity: GranularityType,
): string {
    const headers = [
        "Territoire",
        "Période",
        `Records de chaleur (${kindLabel})`,
        `Records de froid (${kindLabel})`,
    ].join(",");
    const rows = territoryPlots.flatMap(({ name, hot, cold }) => {
        const hotByPeriod = countByPeriod(hot, granularity);
        const coldByPeriod = countByPeriod(cold, granularity);
        const periods = [
            ...new Set([
                ...Object.keys(hotByPeriod),
                ...Object.keys(coldByPeriod),
            ]),
        ].sort();
        return periods.map((period) =>
            [
                escapeCsvValue(name),
                period,
                hotByPeriod[period] ?? 0,
                coldByPeriod[period] ?? 0,
            ].join(","),
        );
    });
    return [headers, ...rows].join("\n");
}

export function buildScatterRecordsCsv(
    records: TemperatureRecordsGraphRecord[],
    type: "hot" | "cold",
    kindLabel: string,
): string {
    const typeLabel = type === "hot" ? "chaleur" : "froid";
    const headers = [
        "Date",
        `Température record de ${typeLabel} (${kindLabel}) (°C)`,
        "Station",
        "Département",
    ].join(",");
    const rows = records
        .filter((r) => r.type_records === type)
        .map((r) =>
            [
                r.date,
                r.valeur,
                escapeCsvValue(r.station_name),
                escapeCsvValue(r.department),
            ].join(","),
        );
    return [headers, ...rows].join("\n");
}
