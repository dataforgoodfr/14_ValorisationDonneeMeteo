import type {
    NationalIndicatorParams,
    NationalIndicatorResponse,
} from "~/types/api";
import type {
    ChartType,
    GranularityType,
    SliceType,
} from "~/components/ui/commons/selectBar/types";
import { fetchStackedData } from "~/utils/itn/nationalIndicatorFetcher";
import { fetchNationalIndicatorForYear } from "~/utils/itn/nationalIndicatorFetcher.real";
import {
    getFirstDayOfMonth,
    getFirstDayOfYearInLocal,
    getLastAvailableDayOfMonth,
    getLastAvailableDayOfYearInLocal,
} from "~/utils/date";

const dates = useCustomDate();

export const useItnStore = defineStore("itnStore", () => {
    const itnChartRef = shallowRef();

    // Date de début et date de fin
    const pickedDateStart = ref(dates.lastYear.value);
    const pickedDateEnd = ref(dates.yesterday.value);
    const maxDate = ref(dates.yesterday.value);

    const granularity: Ref<GranularityType> = ref<GranularityType>("day");
    const sliceTypeSwitchEnabled = ref(false);
    const sliceType: Ref<SliceType> = ref<SliceType>("full");

    const sliceDatepickerDate = ref(new Date(2006, 0, 1));

    const chartType = ref<ChartType>("line");

    // Stacked mode: années sélectionnées et données fusionnées
    const currentYear = new Date().getFullYear();
    // Show the last 3 years by default to show the user the value of the stacked mode.
    const selectedYears = ref<number[]>([
        currentYear - 2,
        currentYear - 1,
        currentYear,
    ]);
    const stackedData = ref<NationalIndicatorResponse | null>(null);
    const stackedPending = ref(false);
    const stackedDataCache = new Map<number, NationalIndicatorResponse>();

    const generateStackedData = async (): Promise<void> => {
        stackedPending.value = true;
        stackedData.value = await fetchStackedData(
            selectedYears.value,
            granularity.value,
            stackedDataCache,
            (year, granularity) =>
                fetchNationalIndicatorForYear(year, granularity),
        );
        stackedPending.value = false;
    };

    watch(
        () => [...selectedYears.value],
        async () => {
            if (chartType.value === "stacked") {
                await generateStackedData();
            }
        },
    );

    watch(granularity, async () => {
        if (chartType.value === "stacked") {
            stackedDataCache.clear();
            await generateStackedData();
        }
    });

    watch(chartType, async (val) => {
        if (val === "stacked") {
            await generateStackedData();
        }
    });

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
        granularity.value =
            chartType.value === "stacked" && value === "year" ? "month" : value;
        if (value === "day") {
            sliceTypeSwitchEnabled.value = false;
            pickedDateStart.value = dates.lastYear.value;
            pickedDateEnd.value = dates.yesterday.value;
        }
        if (value === "month") {
            pickedDateStart.value = dates.lastYear.value;
            pickedDateEnd.value = dates.lastMonth.value;
        }
        if (value === "year") {
            pickedDateStart.value = dates.absoluteMinDataDate.value;
            pickedDateEnd.value = dates.lastYear.value;
        }
    };

    const setChartType = (value: ChartType) => {
        chartType.value = value;
        if (value === "stacked") {
            granularity.value = "day";
            sliceTypeSwitchEnabled.value = false;
            sliceType.value = "full";
        }
    };

    const turnOffSliceType = (value: boolean) => {
        if (!value) {
            sliceType.value = "full";
        }
    };

    const effectiveDateStart = computed(() => {
        if (granularity.value === "year")
            return getFirstDayOfYearInLocal(pickedDateStart.value);
        if (granularity.value === "month")
            return getFirstDayOfMonth(pickedDateStart.value);
        return pickedDateStart.value;
    });

    const effectiveDateEnd = computed(() => {
        if (granularity.value === "year")
            return getLastAvailableDayOfYearInLocal(pickedDateEnd.value);
        if (granularity.value === "month")
            return getLastAvailableDayOfMonth(pickedDateEnd.value);
        return pickedDateEnd.value;
    });

    const params = computed<NationalIndicatorParams>(() => ({
        date_start: dateToStringYMD(effectiveDateStart.value),
        date_end: dateToStringYMD(effectiveDateEnd.value),
        granularity: granularity.value,
        slice_type: sliceType.value,
        month_of_year: month_of_year.value,
        day_of_month: day_of_month.value,
    }));

    const { data: itnData, pending, error } = useNationalIndicator(params);

    const effectiveData = computed(() =>
        chartType.value === "stacked"
            ? (stackedData.value ?? undefined)
            : (itnData.value ?? undefined),
    );
    const effectivePending = computed(() =>
        chartType.value === "stacked" ? stackedPending.value : pending.value,
    );

    return {
        itnChartRef,
        pickedDateStart,
        pickedDateEnd,
        maxDate,
        granularity,
        sliceTypeSwitchEnabled,
        sliceType,
        sliceDatepickerDate,
        month_of_year,
        day_of_month,
        chartType,
        selectedYears,
        setGranularity,
        setChartType,
        turnOffSliceType,
        itnData,
        effectiveData,
        effectivePending,
        effectiveDateStart,
        effectiveDateEnd,
        pending,
        error,
    };
});
