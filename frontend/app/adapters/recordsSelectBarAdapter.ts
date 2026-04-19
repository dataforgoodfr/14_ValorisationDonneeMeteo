import type { SelectBarAdapter } from "~/components/ui/commons/selectBar/types";
import type { TemperatureRecordsResponse } from "~/types/api";

export const useRecordsSelectBarAdapter =
    (): SelectBarAdapter<TemperatureRecordsResponse> => {
        const store = useRecordsChartStore();

        const {
            recordsChartRef,
            granularity,
            pickedDateStart,
            pickedDateEnd,
            maxDate,
            sliceTypeSwitchEnabled, // Will be enabled in futur version
            sliceType, // Will be enabled in futur version
            sliceDatepickerDate, // Will be enabled in futur version
            selectedElements,
            recordsData,
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
            selectedElements,
            chartRef: recordsChartRef,
            data: recordsData,
            pending,
            chartTypeSwitchEnabled,
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
            features: {
                hasSliceType: false, // Will be enabled in futur version
                hasChartTypeSelector: true,
                hasExport: true,
            },
            exportConfig: {
                chartName: "records",
                csvHeaders: [],
                getCsvRows: () => undefined,
            },
        };
    };
