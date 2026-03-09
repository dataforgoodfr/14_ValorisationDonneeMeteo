import type { NationalIndicatorParams } from "~/types/api";
import { useCustomDate } from "#imports";

const dates = useCustomDate();

export const useItnStore = defineStore("itnStore", () => {
    const picked_date_start = ref(dates.lastYear.value);
    const picked_date_end = ref(dates.twoDaysAgo.value);

    const granularity = ref("month" as "year" | "month" | "day");
    const sliceTypeSwitchEnabled = ref(false);
    const slice_type = ref<"full" | "month_of_year" | "day_of_month">("full");

    const sliceDatepickerDate = ref(new Date(2006, 0, 1));

    const month_of_year = computed<undefined | number>(() =>
        granularity.value === "year" && slice_type.value !== "full"
            ? sliceDatepickerDate.value.getMonth() + 1
            : undefined,
    );

    const day_of_month = computed<undefined | number>(() =>
        slice_type.value === "day_of_month"
            ? sliceDatepickerDate.value.getDate()
            : undefined,
    );

    const setGranularity = (value: string) => {
        slice_type.value = "full";
        granularity.value = value as "year" | "month" | "day";
        if (value === "day") {
            sliceTypeSwitchEnabled.value = false;
        }
    };

    const params = computed<NationalIndicatorParams>(() => ({
        date_start: picked_date_start.value.toISOString().substring(0, 10),
        date_end: picked_date_end.value.toISOString().substring(0, 10),
        granularity: granularity.value,
        slice_type: slice_type.value,
        month_of_year: month_of_year.value,
        day_of_month: day_of_month.value,
    }));

    const { data: itnData, pending, error } = useNationalIndicator(params);

    return {
        picked_date_start,
        picked_date_end,
        granularity,
        sliceTypeSwitchEnabled,
        slice_type,
        sliceDatepickerDate,
        month_of_year,
        day_of_month,
        setGranularity,
        itnData,
        pending,
        error,
    };
});
