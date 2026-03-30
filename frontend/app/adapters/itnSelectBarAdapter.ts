import type { SelectBarAdapter } from "~/components/ui/commons/selectBar/types";
import type { NationalIndicatorResponse } from "~/types/api";
import { useItnStore } from "#imports";

export const useItnSelectBarAdapter =
    (): SelectBarAdapter<NationalIndicatorResponse> => {
        const store = useItnStore();

        const {
            itnChartRef,
            granularity,
            pickedDateStart,
            pickedDateEnd,
            sliceTypeSwitchEnabled,
            sliceType,
            sliceDatepickerDate,
            itnData,
            pending,
        } = storeToRefs(store);

        return {
            granularity,
            pickedDateStart,
            pickedDateEnd,
            sliceTypeSwitchEnabled,
            sliceType,
            sliceDatepickerDate,
            chartRef: itnChartRef,
            data: itnData,
            pending,
            setGranularity: store.setGranularity,
            turnOffSliceType: store.turnOffSliceType,
            features: {
                hasSliceType: true,
                hasChartTypeSelector: false,
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
