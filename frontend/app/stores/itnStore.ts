import type { NationalIndicatorParams } from "~/types/api";
import { useCustomDate } from "#imports";



const dates = useCustomDate()

export const useItnStore = defineStore('itnStore', () => {

    const picked_date_start = ref(dates.lastYear.value);
    const picked_date_end = ref(dates.twoDaysAgo.value);

    const granularity = ref("month" as "year" | "month" | "day")
    const slice_type = ref<undefined | "full" | "month_of_year" | "day_of_month">(undefined)
    const month_of_year = ref<undefined | number>(undefined)
    const day_of_month = ref<undefined | number>(undefined)

    const params = computed<NationalIndicatorParams>(() => ({
        date_start: picked_date_start.value.toISOString().substring(0, 10),
        date_end: picked_date_end.value.toISOString().substring(0, 10),
        granularity: granularity.value,
        slice_type: slice_type.value,
        month_of_year: month_of_year.value,
        day_of_month: day_of_month.value,
    }));


    const { data: itnData, pending, error } = useNationalIndicator(params);

    return { picked_date_start, picked_date_end, granularity, slice_type, month_of_year, day_of_month, itnData, pending, error }
})
