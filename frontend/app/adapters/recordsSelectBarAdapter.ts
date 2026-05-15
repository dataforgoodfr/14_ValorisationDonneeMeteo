import type { SelectBarAdapter } from "~/components/ui/commons/selectBar/types";
import type { TemperatureRecordsGraphResponse } from "~/types/api";
import { useRecordsChartStore } from "#imports";
import { buildTerritoryPlots, countByPeriod } from "~/utils/recordsChartUtils";
import { escapeCsvValue } from "~/utils/string";
import { downloadCSV } from "~/utils/csv";
import { useFormatFileName } from "~/composables/useFormatFilename";

export const useRecordsSelectBarAdapter =
    (): SelectBarAdapter<TemperatureRecordsGraphResponse> => {
        const store = useRecordsChartStore();

        const {
            recordsChartRef,
            granularity,
            pickedDateStart,
            pickedDateEnd,
            maxDate,
            sliceTypeSwitchEnabled,
            periodType,
            month,
            season,
            selectedElements,
            processedRecordsData,
            recordKind,
            pending,
            chartType,
        } = storeToRefs(store);

        return {
            granularity,
            pickedDateStart,
            pickedDateEnd,
            maxDate,
            sliceTypeSwitchEnabled,
            sliceTypeSwitchLabel: "Records mensuels/saisonniers",
            analysisPeriodInfoText:
                "Sélectionnez une période pour afficher les records mensuels ou saisonnier.",
            periodType,
            month,
            season,
            selectedElements,
            chartRef: recordsChartRef,
            data: processedRecordsData,
            recordKind,
            pending,
            chartType,
            chartTypeOptions: [
                {
                    label: "Pyramide",
                    value: "pyramid",
                    icon: "i-lucide-chart-bar",
                },
                {
                    label: "Nuage de points",
                    value: "scatter",
                    icon: "i-lucide-chart-scatter",
                },
            ],
            setGranularity: store.setGranularity,
            setChartType: store.setChartType,
            turnOffSliceType: store.turnOffSliceType,
            features: {
                hasSliceType: false,
                hasRecordsPeriodSlice: true,
                hasChartTypeSelector: true,
                hasExport: true,
            },
            exportConfig: {
                chartName: "records",
                csvHeaders: [],
                getCsvRows: () => undefined,
                get htmlTooltipFormatter(): string | undefined {
                    if (chartType.value !== "scatter") return undefined;
                    return `function(params) {
                        if (!Array.isArray(params)) params = [params];
                        if (!params.length) return '';
                        const data = params[0].value;
                        if (!data) return '';
                        const date = new Date(data.date).toLocaleDateString('fr-FR', {day:'2-digit',month:'2-digit',year:'numeric'});
                        const lines = [date];
                        params.forEach((p) => {
                            const v = p.value;
                            if (v && v.value != null) {
                                lines.push((p.marker||'') + ' ' + (v.station||'') + ' : ' + v.value + '°C');
                            }
                        });
                        return lines.join('<br/>');
                    }`;
                },
                onExportCsv: () => {
                    if (!import.meta.client) return;
                    const data = processedRecordsData.value;
                    if (!data) return;

                    const kind = recordKind.value;
                    const kindLabel =
                        kind === "historical"
                            ? "records battus"
                            : "records absolus";
                    const kindFileLabel =
                        kind === "historical" ? "battus" : "absolus";

                    if (chartType.value === "pyramid") {
                        const territoryPlots = buildTerritoryPlots(
                            selectedElements.value,
                            data,
                        );
                        const headers = [
                            "Territoire",
                            "Période",
                            `Records de chaleur (${kindLabel})`,
                            `Records de froid (${kindLabel})`,
                        ].join(",");
                        const rows = territoryPlots.flatMap(
                            ({ name, hot, cold }) => {
                                const hotByPeriod = countByPeriod(
                                    hot,
                                    granularity.value,
                                );
                                const coldByPeriod = countByPeriod(
                                    cold,
                                    granularity.value,
                                );
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
                            },
                        );
                        downloadCSV(
                            [headers, ...rows].join("\n"),
                            useFormatFileName(
                                `records-pyramide-${kindFileLabel}`,
                                granularity.value,
                                "csv",
                                pickedDateStart.value,
                                pickedDateEnd.value,
                            ),
                        );
                    } else {
                        for (const type of ["hot", "cold"] as const) {
                            const typeLabel =
                                type === "hot" ? "chaleur" : "froid";
                            const headers = [
                                "Date",
                                `Température record de ${typeLabel} (${kindLabel}) (°C)`,
                                "Station",
                                "Département",
                            ].join(",");
                            const rows = data.records
                                .filter((r) => r.type_records === type)
                                .map((r) =>
                                    [
                                        r.date,
                                        r.valeur,
                                        escapeCsvValue(r.station_name),
                                        escapeCsvValue(r.department),
                                    ].join(","),
                                );
                            downloadCSV(
                                [headers, ...rows].join("\n"),
                                useFormatFileName(
                                    `records-${typeLabel}-${kindFileLabel}`,
                                    granularity.value,
                                    "csv",
                                    pickedDateStart.value,
                                    pickedDateEnd.value,
                                ),
                            );
                        }
                    }
                },
            },
        };
    };
