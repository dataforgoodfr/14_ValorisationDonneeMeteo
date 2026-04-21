import type { SelectBarAdapter } from "~/components/ui/commons/selectBar/types";
import type { TemperatureRecordsGraphResponse } from "~/types/api";
import { useRecordsChartStore } from "#imports";

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
            sliceTypeSwitchLabel: "Période",
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
            },
        };
    };
