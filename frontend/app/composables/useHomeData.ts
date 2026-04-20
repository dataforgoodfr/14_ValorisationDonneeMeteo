import type { NationalIndicatorParams } from "~/types/api";

const { yesterday, yesterdayLastYear } = useCustomDate();

function generateNationalIndicatorParams(date: Date): NationalIndicatorParams {
    return {
        date_start: dateToStringYMD(date),
        date_end: dateToStringYMD(date),
        granularity: "day",
        slice_type: "full",
    };
}

export function useHomeData() {
    // Yesterday data
    const { data: yesterdayData } = useNationalIndicator(
        generateNationalIndicatorParams(yesterday.value),
    );

    const yesterdayTemperature = computed(
        () => yesterdayData.value?.time_series[0]?.temperature,
    );

    const gap = computed(() => {
        const result = yesterdayData.value?.time_series[0];
        return result ? result.temperature - result.baseline_mean : undefined;
    });

    const { data: yesterdayLastYearData } = useNationalIndicator(
        generateNationalIndicatorParams(yesterdayLastYear.value),
    );

    const temperatureChangeYearOverYear = computed<number | undefined>(() => {
        const lastYearTemperature =
            yesterdayLastYearData.value?.time_series[0]?.temperature;
        if (
            typeof yesterdayTemperature.value !== "number" ||
            typeof lastYearTemperature !== "number"
        ) {
            return undefined;
        }
        return lastYearTemperature - yesterdayTemperature.value;
    });

    return {
        yesterday,
        yesterdayTemperature,
        gap,
        temperatureChangeYearOverYear,
        yesterdayLastYear,
    };
}
