import type { SelectBarAdapter } from "~/components/ui/commons/selectBar/types";
import type { DeviationResponse } from "~/types/api";
import { useDeviationStore } from "#imports";

export const useDeviationSelectBarAdapter =
    (): SelectBarAdapter<DeviationResponse> => {
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
            features: {
                hasSliceType: false, // Will be enabled in futur version
                hasChartTypeSelector: false,
                hasExport: true,
            },
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
