import type { NationalIndicatorParams } from "~/types/api";
import { useCustomDate } from "#imports";
import type {
    GranularityType,
    SliceType,
} from "~/components/ui/commons/selectBar/types";

const dates = useCustomDate();

export const useItnStore = defineStore("itnStore", () => {
    const itnChartRef = shallowRef();

    // Date de début et date de fin
    const pickedDateStart = ref(dates.lastYear.value);
    const pickedDateEnd = ref(dates.twoDaysAgo.value);

    const granularity: Ref<GranularityType> = ref<GranularityType>("month");
    const sliceTypeSwitchEnabled = ref(false);
    const sliceType: Ref<SliceType> = ref<SliceType>("full");

    const sliceDatepickerDate = ref(new Date(2006, 0, 1));

    const month_of_year = computed<undefined | number>(() =>
        granularity.value === "year" && sliceType.value !== "full"
            ? sliceDatepickerDate.value.getMonth() + 1
            : undefined,
    );

    const day_of_month = computed<undefined | number>(() =>
        sliceType.value === "day_of_month"
            ? sliceDatepickerDate.value.getDate()
            : undefined,
    );

    const setGranularity = (value: GranularityType) => {
        sliceType.value = "full";
        granularity.value = value;
        if (value === "day") {
            sliceTypeSwitchEnabled.value = false;
        }
    };

    const turnOffSliceType = (value: boolean) => {
        if (!value) {
            sliceType.value = "full";
        }
    };

    const params = computed<NationalIndicatorParams>(() => ({
        date_start: pickedDateStart.value
            .toISOString()
            .substring(0, "YYYY-MM-DD".length),
        date_end: pickedDateEnd.value
            .toISOString()
            .substring(0, "YYYY-MM-DD".length),
        granularity: granularity.value,
        slice_type: sliceType.value,
        month_of_year: month_of_year.value,
        day_of_month: day_of_month.value,
    }));

    const { data: itnData, pending, error } = useNationalIndicator(params);

    return {
        itnChartRef,
        pickedDateStart,
        pickedDateEnd,
        granularity,
        sliceTypeSwitchEnabled,
        sliceType,
        sliceDatepickerDate,
        month_of_year,
        day_of_month,
        setGranularity,
        turnOffSliceType,
        itnData,
        pending,
        error,
    };
});
