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
        };
    };
