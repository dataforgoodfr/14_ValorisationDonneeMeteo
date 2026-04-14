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
                    "Date",
                    "Écart à la normale en °C",
                    "Température observée en °C",
                    "Température de référence 1991-2020 en °C",
                ],
                getCsvRows: () => deviationData.value?.national.data,
            },
        };
    };
