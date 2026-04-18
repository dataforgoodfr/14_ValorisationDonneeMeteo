import type {
    NationalIndicatorParams,
    NationalIndicatorResponse,
} from "~/types/api";
import { useCustomDate, dateToStringYMD } from "#imports";
import type {
    GranularityType,
    SliceType,
    ChartType,
} from "~/components/ui/commons/selectBar/types";
import { fetchNationalIndicatorForYear } from "~/utils/nationalIndicatorFetcher";

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
    const selectedYears = ref<number[]>([new Date().getFullYear()]);
    const stackedData = ref<NationalIndicatorResponse | null>(null);
    const stackedPending = ref(false);
    const stackedDataCache = new Map<number, NationalIndicatorResponse>();

    const { apiFetch } = useApiClient();

    async function fetchStackedData(): Promise<void> {
        if (selectedYears.value.length === 0) {
            stackedData.value = null;
            return;
        }
        stackedPending.value = true;

        try {
            const responses = await Promise.all(
                selectedYears.value.map(async (year) => {
                    if (stackedDataCache.has(year)) {
                        return stackedDataCache.get(year);
                    }

                    const result = await fetchNationalIndicatorForYear(
                        apiFetch,
                        year,
                        granularity.value,
                    );

                    stackedDataCache.set(year, result);

                    return result;
                }),
            );

            stackedData.value = {
                metadata: responses[0]!.metadata,
                time_series: responses.flatMap((r) => r.time_series),
            };
        } catch {
            stackedData.value = null;
        } finally {
            stackedPending.value = false;
        }
    }

    watch(
        [selectedYears, granularity],
        () => {
            if (chartType.value === "stacked") fetchStackedData();
        },
        { deep: true },
    );

    watch(chartType, (val) => {
        if (val === "stacked") fetchStackedData();
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
            maxDate.value = dates.yesterday.value;
        }
        if (value === "month") {
            pickedDateStart.value = dates.last10Year.value;
            pickedDateEnd.value = dates.lastMonth.value;
            maxDate.value = dates.lastMonth.value;
        }
        if (value === "year") {
            pickedDateStart.value = dates.absoluteMinDataDate.value;
            pickedDateEnd.value = dates.lastYear.value;
            maxDate.value = dates.lastYear.value;
        }
    };

    const setChartType = (value: ChartType) => {
        chartType.value = value;
        if (value === "stacked") {
            if (granularity.value === "year") granularity.value = "month";
            sliceTypeSwitchEnabled.value = false;
            sliceType.value = "full";
        }
    };

    const turnOffSliceType = (value: boolean) => {
        if (!value) {
            sliceType.value = "full";
        }
    };

    const params = computed<NationalIndicatorParams>(() => ({
        date_start: dateToStringYMD(pickedDateStart.value),
        date_end: dateToStringYMD(pickedDateEnd.value),
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
        pending,
        error,
    };
});
