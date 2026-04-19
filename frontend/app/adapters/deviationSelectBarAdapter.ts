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
            sliceTypeSwitchEnabled, // Will be enabled in futur version
            sliceType, // Will be enabled in futur version
            sliceDatepickerDate, // Will be enabled in futur version
            deviationData,
            pending,
            chartTypeSwitchEnabled,
            chartType,
        } = storeToRefs(store);

        return {
            granularity,
            pickedDateStart,
            pickedDateEnd,
            maxDate,
            sliceTypeSwitchEnabled, // Will be enabled in futur version
            sliceType, // Will be enabled in futur version
            sliceDatepickerDate, // Will be enabled in futur version
            chartRef: deviationChartRef,
            data: deviationData,
            pending,
            setGranularity: store.setGranularity,
            chartType,
            chartTypeSwitchEnabled,
            setChartType: store.setChartType,
            features: {
                hasSliceType: false, // Will be enabled in futur version
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
                                deviation: point.deviation,
                                temperature: point.temperature,
                                baseline_mean: point.baseline_mean,
                            })),
                        );
                },
            },
        };
    };
