import type {
    PeriodType,
    TemperatureRecordsPaginatedResponse,
    TypeRecords,
} from "~/types/api";

export function useExportRecordsBattus() {
    const { apiFetch } = useApiClient();

    async function exportRecords(
        typeRecords: TypeRecords,
        dateStart: string,
        dateEnd: string,
        period: PeriodType,
    ) {
        if (!import.meta.client) return;

        const data = await apiFetch<TemperatureRecordsPaginatedResponse>(
            "/temperature/records",
            {
                query: {
                    type_records: typeRecords,
                    period_type: period,
                    date_start: dateStart,
                    date_end: dateEnd,
                    page_size: 9999,
                },
            },
        );

        const label = typeRecords === "hot" ? "chaud" : "froid";
        downloadCSV(
            buildRecordsCsv(data.results, "Record (°C)"),
            useFormatFileName(
                `records-battus-${label}`,
                `${dateStart}_${dateEnd}`,
                "csv",
            ),
        );
    }

    return { exportRecords };
}
