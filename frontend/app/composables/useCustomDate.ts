import {
    CalendarDate,
    DateFormatter,
    getLocalTimeZone,
} from "@internationalized/date";

export function useCustomDate() {

    // Return only month and year : (YYYY, M)
    const monthYearDisplay = (date: CalendarDate) => {
        const dateFormatterYYYMM = new DateFormatter("en-US", {
            year: "numeric",
            month: "long",
        });
        return dateFormatterYYYMM.format(date.toDate(getLocalTimeZone()));
    };
    const todayYYYYMD = computed(() => {
        const today = new Date();
        return new CalendarDate(today.getFullYear(), today.getMonth() + 1, 1);
    });

    const twoDaysAgoYYYMD = computed(() => {
        const twoDaysAgoDate = new Date();
        return new CalendarDate(twoDaysAgoDate.getFullYear(), twoDaysAgoDate.getMonth() + 1, twoDaysAgoDate.getDate() - 2);
    });

    const lastYearYYYYMD = computed(() => {
        const today = new Date();
        return new CalendarDate(today.getFullYear() - 1, today.getMonth() + 1, 1);
    });

    const absoluteMinDataDateYYYYMD = computed(() => new CalendarDate(1946, 1, 1));

    return {
        monthYearDisplay, todayYYYYMD, twoDaysAgoYYYMD, lastYearYYYYMD, absoluteMinDataDateYYYYMD
    };
}
