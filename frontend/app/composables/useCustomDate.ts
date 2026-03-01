export function useCustomDate() {

    const twoDaysAgo = computed(() => {
        const todayDate = new Date();
        todayDate.setDate(todayDate.getDate() - 2)

        return new Date(todayDate)
    });

    const lastYear = computed(() => {
        const todayDate = new Date();
        todayDate.setFullYear(todayDate.getFullYear() - 1)

        return new Date(todayDate)
    });

    const absoluteMinDataDate = computed(() => {
        const minDataDate = new Date(1946, 0, 1)

        return minDataDate
    });

    return {
        twoDaysAgo, lastYear, absoluteMinDataDate
    };
}
