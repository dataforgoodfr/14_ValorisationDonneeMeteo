import { CalendarDate } from "@internationalized/date";
import type { NationalIndicatorParams } from "~/types/api";
import { useCustomDate } from "#imports";

// Stores a CalendarDate as a serializable POJO ref, exposes it as a writable computed.
// Required because Pinia serializes ref state for SSR and CalendarDate is not a POJO.
function calendarDateRef(initial: CalendarDate) {
    const raw = ref({ year: initial.year, month: initial.month, day: initial.day });
    return computed<CalendarDate>({
        get: () => new CalendarDate(raw.value.year, raw.value.month, raw.value.day),
        set: (val) => { raw.value = { year: val.year, month: val.month, day: val.day } },
    });
}

const dates = useCustomDate()

export const useItnStore = defineStore('itnStore', () => {

    const picked_date_start = calendarDateRef(dates.lastYearYYYYMD.value);
    const picked_date_end = calendarDateRef(dates.twoDaysAgoYYYMD.value);

    const granularity = ref("month" as "year" | "month" | "day")
    const slice_type = ref<undefined | "full" | "month_of_year" | "day_of_month">(undefined)
    const month_of_year = ref<undefined | number>(undefined)
    const day_of_month = ref<undefined | number>(undefined)

    const params = computed<NationalIndicatorParams>(() => ({
        date_start: picked_date_start.value.toString(),
        date_end: picked_date_end.value.toString(),
        granularity: granularity.value,
        slice_type: slice_type.value,
        month_of_year: month_of_year.value,
        day_of_month: day_of_month.value,
    }));

    const { data: itnData, pending, error } = useNationalIndicator(params);

    return { picked_date_start, picked_date_end, granularity, slice_type, month_of_year, day_of_month, itnData, pending, error }
})
