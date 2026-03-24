import type { SelectBarAdapter } from "~/components/ui/commons/selectBar/types";
import type { DeviationResponse } from "~/types/api";

export const useDeviationSelectBarAdapter =
    (): SelectBarAdapter<DeviationResponse> => {
        const store = useDeviationStore();

        const {
            granularity,
            pickedDateStart,
            pickedDateEnd,
            sliceTypeSwitchEnabled,
            sliceType,
            sliceDatepickerDate,
            chartTypeSwitchEnabled,
            deviationData,
            pending,
        } = storeToRefs(store);

        return {
            granularity,
            pickedDateStart,
            pickedDateEnd,
            sliceTypeSwitchEnabled,
            sliceType,
            sliceDatepickerDate,
            chartTypeSwitchEnabled,
            data: deviationData,
            pending,
            setGranularity: store.setGranularity,
            setChartType: store.setChartType,
            features: {
                hasSliceType: true,
                hasChartTypeSelector: true,
                hasExport: false,
            },
        };
    };
