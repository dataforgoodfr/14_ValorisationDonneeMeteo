import type { NationalIndicatorParams } from "~/types/api";

const { yesterday } = useCustomDate();

export function useHomeData() {
    // Yesterday data
    const yesterdayParams = computed<NationalIndicatorParams>(() => {
        return {
            date_start: dateToStringYMD(yesterday.value),
            date_end: dateToStringYMD(yesterday.value),
            granularity: "day",
            slice_type: "full",
        };
    });
    const { data: yesterdayData } = useNationalIndicator(yesterdayParams);

    const yesterdayTemperature = computed(
        () => yesterdayData.value?.time_series[0]?.temperature,
    );

    const gap = computed(() => {
        const result = yesterdayData.value?.time_series[0];
        return result ? result.temperature - result.baseline_mean : undefined;
    });

    // Yesterday Last Year data
    const yesterdayLastYear = computed(() => {
        const date = new Date(yesterday.value);
        date.setFullYear(date.getFullYear() - 1);
        return date;
    });
    const yesterdayLastYearParams = computed<NationalIndicatorParams>(() => {
        return {
            date_start: dateToStringYMD(yesterdayLastYear.value),
            date_end: dateToStringYMD(yesterdayLastYear.value),
            granularity: "day",
            slice_type: "full",
        };
    });
    const { data: yesterdayLastYearData } = useNationalIndicator(
        yesterdayLastYearParams,
    );

    const temperatureChangeYearOverYear = computed(() => {
        if (
            !yesterdayTemperature.value ||
            !yesterdayLastYearData.value?.time_series[0]?.temperature
        ) {
            return undefined;
        }
        return (
            yesterdayLastYearData.value?.time_series[0]?.temperature -
            yesterdayTemperature.value
        );
    });

    return {
        yesterday,
        yesterdayTemperature,
        gap,
        temperatureChangeYearOverYear,
        yesterdayLastYear,
    };
}
