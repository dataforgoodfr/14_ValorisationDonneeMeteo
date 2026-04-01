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

    const _params = computed<NationalIndicatorParams>(() => ({
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

    // MOCK: short-circuit API call for testing

    const mockData = {
        metadata: {
            date_start: "2025-11-30",
            date_end: "2026-01-29",
            baseline: "1991-2020",
            granularity: "day" as const,
            slice_type: "full" as const,
        },
        time_series: [
            {
                date: "2025-11-30",
                temperature: 7.54,
                baseline_mean: 7.01,
                baseline_std_dev_upper: 9.83,
                baseline_std_dev_lower: 4.2,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2025-12-01",
                temperature: 5.59,
                baseline_mean: 6.87,
                baseline_std_dev_upper: 9.71,
                baseline_std_dev_lower: 4.03,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2025-12-02",
                temperature: 7.41,
                baseline_mean: 6.91,
                baseline_std_dev_upper: 9.79,
                baseline_std_dev_lower: 4.04,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2025-12-03",
                temperature: 7.71,
                baseline_mean: 6.95,
                baseline_std_dev_upper: 10.05,
                baseline_std_dev_lower: 3.85,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2025-12-04",
                temperature: 7.13,
                baseline_mean: 6.99,
                baseline_std_dev_upper: 10.04,
                baseline_std_dev_lower: 3.93,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2025-12-05",
                temperature: 6.76,
                baseline_mean: 6.8,
                baseline_std_dev_upper: 9.68,
                baseline_std_dev_lower: 3.92,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2025-12-06",
                temperature: 9.26,
                baseline_mean: 6.67,
                baseline_std_dev_upper: 9.61,
                baseline_std_dev_lower: 3.73,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2025-12-07",
                temperature: 11.96,
                baseline_mean: 6.44,
                baseline_std_dev_upper: 9.47,
                baseline_std_dev_lower: 3.41,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2025-12-08",
                temperature: 12.8,
                baseline_mean: 6.66,
                baseline_std_dev_upper: 9.43,
                baseline_std_dev_lower: 3.88,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2025-12-09",
                temperature: 11.66,
                baseline_mean: 6.19,
                baseline_std_dev_upper: 8.97,
                baseline_std_dev_lower: 3.41,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2025-12-10",
                temperature: 11.71,
                baseline_mean: 5.87,
                baseline_std_dev_upper: 8.6,
                baseline_std_dev_lower: 3.15,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2025-12-11",
                temperature: 9.52,
                baseline_mean: 5.88,
                baseline_std_dev_upper: 8.67,
                baseline_std_dev_lower: 3.09,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2025-12-12",
                temperature: 9.88,
                baseline_mean: 6.04,
                baseline_std_dev_upper: 9.05,
                baseline_std_dev_lower: 3.02,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2025-12-13",
                temperature: 8.2,
                baseline_mean: 5.97,
                baseline_std_dev_upper: 8.8,
                baseline_std_dev_lower: 3.14,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2025-12-14",
                temperature: 6.83,
                baseline_mean: 5.41,
                baseline_std_dev_upper: 8.65,
                baseline_std_dev_lower: 2.18,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2025-12-15",
                temperature: 8.88,
                baseline_mean: 5.22,
                baseline_std_dev_upper: 8.58,
                baseline_std_dev_lower: 1.85,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2025-12-16",
                temperature: 10.14,
                baseline_mean: 5.69,
                baseline_std_dev_upper: 9.04,
                baseline_std_dev_lower: 2.35,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2025-12-17",
                temperature: 8.5,
                baseline_mean: 6.02,
                baseline_std_dev_upper: 9.26,
                baseline_std_dev_lower: 2.79,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2025-12-18",
                temperature: 10.53,
                baseline_mean: 6.24,
                baseline_std_dev_upper: 9.61,
                baseline_std_dev_lower: 2.87,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2025-12-19",
                temperature: 10.45,
                baseline_mean: 6.57,
                baseline_std_dev_upper: 10.25,
                baseline_std_dev_lower: 2.88,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2025-12-20",
                temperature: 9.79,
                baseline_mean: 6.23,
                baseline_std_dev_upper: 9.6,
                baseline_std_dev_lower: 2.85,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2025-12-21",
                temperature: 10.17,
                baseline_mean: 6.31,
                baseline_std_dev_upper: 9.43,
                baseline_std_dev_lower: 3.18,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2025-12-22",
                temperature: 7.99,
                baseline_mean: 6.9,
                baseline_std_dev_upper: 10.13,
                baseline_std_dev_lower: 3.66,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2025-12-23",
                temperature: 6.52,
                baseline_mean: 6.85,
                baseline_std_dev_upper: 10.33,
                baseline_std_dev_lower: 3.36,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2025-12-24",
                temperature: 5.07,
                baseline_mean: 6.51,
                baseline_std_dev_upper: 9.9,
                baseline_std_dev_lower: 3.13,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2025-12-25",
                temperature: 3.25,
                baseline_mean: 5.94,
                baseline_std_dev_upper: 9.18,
                baseline_std_dev_lower: 2.7,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2025-12-26",
                temperature: 3.53,
                baseline_mean: 5.02,
                baseline_std_dev_upper: 8.36,
                baseline_std_dev_lower: 1.69,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2025-12-27",
                temperature: 3.85,
                baseline_mean: 5.03,
                baseline_std_dev_upper: 8.58,
                baseline_std_dev_lower: 1.48,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2025-12-28",
                temperature: 3.27,
                baseline_mean: 4.75,
                baseline_std_dev_upper: 8.12,
                baseline_std_dev_lower: 1.37,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2025-12-29",
                temperature: 2.36,
                baseline_mean: 4.59,
                baseline_std_dev_upper: 8.04,
                baseline_std_dev_lower: 1.13,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2025-12-30",
                temperature: 2.66,
                baseline_mean: 5.32,
                baseline_std_dev_upper: 8.74,
                baseline_std_dev_lower: 1.91,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2025-12-31",
                temperature: 1.4,
                baseline_mean: 5.57,
                baseline_std_dev_upper: 9.14,
                baseline_std_dev_lower: 2,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2026-01-01",
                temperature: 0.33,
                baseline_mean: 5.39,
                baseline_std_dev_upper: 9.01,
                baseline_std_dev_lower: 1.77,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2026-01-02",
                temperature: 2.23,
                baseline_mean: 5.56,
                baseline_std_dev_upper: 9.27,
                baseline_std_dev_lower: 1.84,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2026-01-03",
                temperature: 1.07,
                baseline_mean: 5.42,
                baseline_std_dev_upper: 9.31,
                baseline_std_dev_lower: 1.52,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2026-01-04",
                temperature: -0.1,
                baseline_mean: 5.19,
                baseline_std_dev_upper: 9.17,
                baseline_std_dev_lower: 1.21,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2026-01-05",
                temperature: -1.02,
                baseline_mean: 5.35,
                baseline_std_dev_upper: 8.95,
                baseline_std_dev_lower: 1.74,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2026-01-06",
                temperature: -1.22,
                baseline_mean: 5.48,
                baseline_std_dev_upper: 9.12,
                baseline_std_dev_lower: 1.85,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2026-01-21",
                temperature: 7.84,
                baseline_mean: 5.58,
                baseline_std_dev_upper: 8.31,
                baseline_std_dev_lower: 2.85,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2026-01-22",
                temperature: 7.97,
                baseline_mean: 5.58,
                baseline_std_dev_upper: 8.64,
                baseline_std_dev_lower: 2.51,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2026-01-23",
                temperature: 6.91,
                baseline_mean: 5.51,
                baseline_std_dev_upper: 8.49,
                baseline_std_dev_lower: 2.54,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2026-01-24",
                temperature: 5.91,
                baseline_mean: 5.25,
                baseline_std_dev_upper: 8.46,
                baseline_std_dev_lower: 2.04,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2026-01-25",
                temperature: 5.68,
                baseline_mean: 4.89,
                baseline_std_dev_upper: 8.47,
                baseline_std_dev_lower: 1.3,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2026-01-26",
                temperature: 6.08,
                baseline_mean: 4.6,
                baseline_std_dev_upper: 7.93,
                baseline_std_dev_lower: 1.28,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2026-01-27",
                temperature: 6.79,
                baseline_mean: 4.77,
                baseline_std_dev_upper: 7.93,
                baseline_std_dev_lower: 1.61,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2026-01-28",
                temperature: 6.29,
                baseline_mean: 5.11,
                baseline_std_dev_upper: 8.12,
                baseline_std_dev_lower: 2.1,
                baseline_max: 0,
                baseline_min: 0,
            },
            {
                date: "2026-01-29",
                temperature: 6.18,
                baseline_mean: 5.06,
                baseline_std_dev_upper: 7.61,
                baseline_std_dev_lower: 2.52,
                baseline_max: 0,
                baseline_min: 0,
            },
        ],
    };
    const itnData =
        ref<import("~/types/api").NationalIndicatorResponse>(mockData);
    const pending = ref(false);
    const error = ref(null);
    // END MOCK

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
