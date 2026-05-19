import type { SelectBarAdapter } from "~/components/ui/commons/selectBar/types";
import type { TemperatureRecordsGraphResponse } from "~/types/api";
import { useRecordsChartStore } from "#imports";
import { buildTerritoryPlots } from "~/utils/recordsChartUtils";
import {
    getRecordKindLabels,
    buildPyramidRecordsCsv,
    buildScatterRecordsCsv,
} from "~/utils/recordsCsv";
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
            recordsData,
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
            data: recordsData,
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
                    if (chartType.value === "pyramid") {
                        return `function(params) {
                        if (!Array.isArray(params)) params = [params];
                        if (!params.length) return '';
                        const toBar = (v) => Array.isArray(v) ? {period: v[0], hot: v[1], cold: v[2]} : v;
                        const d = toBar(params[0].value);
                        const hotMarker = '<span style="display:inline-block;margin-right:4px;border-radius:10px;width:10px;height:10px;background-color:#d32F2F;"></span>';
                        const coldMarker = '<span style="display:inline-block;margin-right:4px;border-radius:10px;width:10px;height:10px;background-color:#1976D2;"></span>';
                        return ['<b>' + d.period + '</b>', hotMarker + ' Records de chaleur : ' + d.hot, coldMarker + ' Records de froid : ' + d.cold].join('<br/>');
                    }`;
                    }
                    if (chartType.value !== "scatter") return undefined;
                    return `function(params) {
                        if (!Array.isArray(params)) params = [params];
                        if (!params.length) return '';
                        const first = params[0];
                        const toScatter = (v) => Array.isArray(v) ? {date: v[0], value: v[1], station: v[2]} : v;
                        const toBar = (v) => Array.isArray(v) ? {period: v[0], hot: v[1], cold: v[2]} : v;
                        if (first.seriesType === 'bar') {
                            const d = toBar(first.value);
                            const hotMarker = '<span style="display:inline-block;margin-right:4px;border-radius:10px;width:10px;height:10px;background-color:#d32F2F;"></span>';
                            const coldMarker = '<span style="display:inline-block;margin-right:4px;border-radius:10px;width:10px;height:10px;background-color:#1976D2;"></span>';
                            return ['<b>' + d.period + '</b>', hotMarker + ' Records de chaleur : ' + d.hot, coldMarker + ' Records de froid : ' + d.cold].join('<br/>');
                        }
                        const data = toScatter(first.value);
                        if (!data) return '';
                        const date = new Date(data.date).toLocaleDateString('fr-FR', {day:'2-digit',month:'2-digit',year:'numeric'});
                        const lines = [date];
                        params.forEach((p) => {
                            const v = toScatter(p.value);
                            if (v && v.value != null) {
                                lines.push((p.marker||'') + ' ' + (v.station||'') + ' : ' + v.value + '°C');
                            }
                        });
                        return lines.join('<br/>');
                    }`;
                },
                onExportCsv: () => {
                    if (!import.meta.client) return;
                    const data = recordsData.value;
                    if (!data) return;

                    const { kindLabel, kindFileLabel } = getRecordKindLabels(
                        recordKind.value,
                    );

                    if (chartType.value === "pyramid") {
                        const territoryPlots = buildTerritoryPlots(
                            selectedElements.value,
                            data,
                        );
                        downloadCSV(
                            buildPyramidRecordsCsv(
                                territoryPlots,
                                kindLabel,
                                granularity.value,
                            ),
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
                            downloadCSV(
                                buildScatterRecordsCsv(
                                    data.records,
                                    type,
                                    kindLabel,
                                ),
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
