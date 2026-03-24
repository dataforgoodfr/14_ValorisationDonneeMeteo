import type { SelectBarAdapter } from "~/components/ui/commons/selectBar/types";
import type { DeviationResponse } from "~/types/api";
import { useDeviationStore } from "#imports";

export const useDeviationSelectBarAdapter =
    (): SelectBarAdapter<DeviationResponse> => {
        const store = useDeviationStore();

        const {
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
            data: deviationData,
            pending,
            setGranularity: store.setGranularity,
            features: {
                hasSliceType: false, // Will be enabled in futur version
                hasChartTypeSelector: false,
                hasExport: true,
            },
        };
    };
