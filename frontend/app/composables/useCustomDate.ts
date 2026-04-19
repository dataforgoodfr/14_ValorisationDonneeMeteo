export function useCustomDate() {
    const today = computed(() => new Date());

    const yesterday = computed(() => {
        const d = new Date();
        d.setDate(d.getDate() - 1);
        return d;
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

    return {
        today,
        yesterday,
        lastMonth,
        lastYear,
        last10Year,
        absoluteMinDataDate,
    };
}
