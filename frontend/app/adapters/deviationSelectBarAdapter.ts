import type { SelectBarAdapter } from "~/components/ui/commons/selectBar/types";
import type { TemperatureDeviationGraphResponse } from "~/types/api";
import { useDeviationStore } from "#imports";

export const useDeviationSelectBarAdapter =
    (): SelectBarAdapter<TemperatureDeviationGraphResponse> => {
        const store = useDeviationStore();

        const {
            deviationChartRef,
            granularity,
            pickedDateStart,
            pickedDateEnd,
            maxDate,
            sliceTypeSwitchEnabled,
            sliceType,
            sliceDatepickerDate,
            deviationData,
            pending,
            chartTypeSwitchEnabled,
            chartType,
            calendarAverageEnabled,
            calendarSliceMode,
            calendarDatepickerDate,
            isCalendarHeatmap,
        } = storeToRefs(store);

        return {
            granularity,
            pickedDateStart,
            pickedDateEnd,
            maxDate,
            sliceTypeSwitchEnabled,
            sliceType,
            sliceDatepickerDate,
            chartRef: deviationChartRef,
            data: deviationData,
            pending,
            analysisPeriodInfoText:
                "Sélectionnez une période pour afficher les données moyennées sur un mois ou un jour spécifique.",
            setGranularity: store.setGranularity,
            turnOffSliceType: store.turnOffSliceType,
            chartType,
            chartTypeSwitchEnabled,
            setChartType: store.setChartType,
            calendarAverageEnabled,
            calendarSliceMode,
            calendarDatepickerDate,
            isCalendarHeatmap,
            setCalendarAverageEnabled: store.setCalendarAverageEnabled,
            features: {
                hasSliceType: true,
                hasRecordsPeriodSlice: false,
                hasChartTypeSelector: true,
                hasExport: true,
            },
            chartTypeOptions: [
                {
                    label: "Barres",
                    value: "bar",
                    icon: "i-lucide-chart-column",
                },
                {
                    label: "Calendrier",
                    value: "calendar",
                    icon: "i-lucide-calendar-days",
                },
            ],
            exportConfig: {
                chartName: "ecart-normale",
                csvHeaders: [
                    "Station / Territoire",
                    "Date",
                    "Écart à la normale en °C",
                    "Température observée en °C",
                    "Température de référence 1991-2020 en °C",
                ],
                getCsvRows: () => {
                    if (!deviationData.value) return undefined;
                    return store
                        .stationsAndNationalFormatted(deviationData.value)
                        .flatMap((serie) =>
                            serie.data.map((point) => ({
                                station_name: serie.station_name,
                                date: point.date,
                                deviation: point.deviation.toFixed(1),
                                temperature: point.temperature.toFixed(1),
                                baseline_mean: point.baseline_mean.toFixed(1),
                            })),
                        );
                },
            },
        };
    };
