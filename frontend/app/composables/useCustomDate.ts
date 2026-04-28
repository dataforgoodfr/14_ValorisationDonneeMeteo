export function useCustomDate() {
    const today = computed(() => new Date());

    const yesterday = computed(() => {
        const d = new Date();
        d.setDate(d.getDate() - 1);
        return d;
    });

    const yesterdayLess30Days = computed(() => {
        const date = new Date();
        date.setDate(date.getDate() - 30);
        return date;
    });

    const yesterdayLess365Days = computed(() => {
        const date = new Date();
        date.setDate(date.getDate() - 365);
        return date;
    });

    const lastMonth = computed(() => {
        const todayDate = new Date();
        todayDate.setMonth(todayDate.getMonth() - 1);

        return new Date(todayDate);
    });

    const lastYear = computed(() => {
        const todayDate = new Date();
        todayDate.setFullYear(todayDate.getFullYear() - 1);

        return new Date(todayDate);
    });

    const last10Year = computed(() => {
        const todayDate = new Date();
        todayDate.setFullYear(todayDate.getFullYear() - 10);

        return new Date(todayDate);
    });

    const absoluteMinDataDate = computed(() => {
        const minDataDate = new Date(1946, 0, 1);

        return minDataDate;
    });

    const yesterdayLastYear = computed(() => {
        const date = new Date(yesterday.value);
        date.setFullYear(date.getFullYear() - 1);
        return date;
    });

    return {
        today,
        yesterday,
        yesterdayLess30Days,
        yesterdayLess365Days,
        lastMonth,
        lastYear,
        last10Year,
        absoluteMinDataDate,
        yesterdayLastYear,
    };
}
