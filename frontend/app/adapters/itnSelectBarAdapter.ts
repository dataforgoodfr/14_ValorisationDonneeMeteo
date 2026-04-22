import type {
    NationalIndicatorDataPoint,
    NationalIndicatorResponse,
} from "~/types/api";
import type { SelectBarAdapter } from "~/components/ui/commons/selectBar/types";
import { useItnStore } from "#imports";

export const useItnSelectBarAdapter = (): SelectBarAdapter<
    NationalIndicatorResponse,
    NationalIndicatorDataPoint
> => {
    const store = useItnStore();

    const {
        itnChartRef,
        granularity,
        pickedDateStart,
        pickedDateEnd,
        maxDate,
        sliceTypeSwitchEnabled,
        sliceType,
        sliceDatepickerDate,
        itnData,
        chartType,
        selectedYears,
        effectiveData,
        effectivePending,
    } = storeToRefs(store);

    return {
        granularity,
        pickedDateStart,
        pickedDateEnd,
        maxDate,
        sliceTypeSwitchEnabled,
        sliceType,
        sliceDatepickerDate,
        chartRef: itnChartRef,
        data: effectiveData,
        pending: effectivePending,
        chartType,
        selectedYears,
        chartTypeOptions: [
            {
                label: "Continu",
                value: "line",
                icon: "i-lucide-chart-line",
            },
            {
                label: "Superposé",
                value: "stacked",
                icon: "i-lucide-square-stack",
            },
        ],
        setGranularity: store.setGranularity,
        setChartType: store.setChartType,
        turnOffSliceType: store.turnOffSliceType,
        features: {
            hasSliceType: true,
            hasRecordsPeriodSlice: false,
            hasChartTypeSelector: true,
            hasExport: true,
        },
        exportConfig: {
            chartName: "itn",
            csvHeaders: [
                "Date",
                "Température observée en °C (moyenne/valeur selon slice_type)",
                "Température moyenne de référence 1991-2020 pour cette période en °C",
                "Écart-type supérieur en °C (moyenne + 1°C écart-type)",
                "Écart-type inférieur en °C (moyenne - 1°C écart-type)",
                "Température maximale observée sur la période 1991-2020 en °C ",
                "Température minimale observée sur la période 1991-2020 en °C ",
            ],
            getCsvRows: () => itnData.value?.time_series,
        },
    };
};
