import type {
    Station,
    TemperatureDeviationGraphParams,
    TemperatureDeviationGraphResponse,
    TemperatureDeviationGraphStationSerie,
} from "~/types/api";
import type {
    ChartType,
    GranularityType,
    SliceType,
} from "~/components/ui/commons/selectBar/types";
import type { DeviationStationIdAndName } from "~/types/common";
import {
    getFirstDayOfMonth,
    getFirstDayOfYearInLocal,
    getLastAvailableDayOfMonth,
    getLastAvailableDayOfYearInLocal,
} from "~/utils/date";
import { useCustomDate } from "#imports";

const dates = useCustomDate();

export const useDeviationStore = defineStore("deviationStore", () => {
    const deviationChartRef = shallowRef();

    const pickedDateStart = ref(dates.last10Year.value);
    const pickedDateEnd = ref(dates.lastMonth.value);
    const maxDate = ref(dates.yesterday.value);

    const granularity: Ref<GranularityType> = ref<GranularityType>("month");
    const sliceTypeSwitchEnabled = ref(false);
    const sliceType: Ref<SliceType> = ref<SliceType>("full");

    const sliceDatepickerDate = ref(new Date(2006, 0, 1));

    const chartTypeSwitchEnabled = ref(false);
    const chartType: Ref<ChartType> = ref<ChartType>(`bar`);

    const calendarAverageEnabled = ref(false);
    const calendarSliceMode: Ref<"all" | "specific"> = ref("all");
    const calendarDatepickerDate = ref(new Date(2006, 0, 1));

    const calendarSelectedMonth = computed<number | null>(() =>
        calendarAverageEnabled.value &&
        calendarSliceMode.value === "specific" &&
        granularity.value === "year"
            ? calendarDatepickerDate.value.getMonth() + 1
            : null,
    );

    const calendarSelectedDay = computed<number | null>(() =>
        calendarAverageEnabled.value &&
        calendarSliceMode.value === "specific" &&
        granularity.value === "month"
            ? calendarDatepickerDate.value.getDate()
            : null,
    );

    const stationIds = ref<string[]>([]);
    const selectedStations = ref<Station[]>([]);
    const includeNational = ref<boolean>(true);

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

    const calendarEffectiveGranularity = computed<GranularityType>(() => {
        if (!calendarAverageEnabled.value) return granularity.value;
        if (granularity.value === "year") {
            return calendarSelectedMonth.value === null ? "month" : "year";
        }
        return calendarSelectedDay.value === null ? "day" : "month";
    });

    const calendarEffectiveSliceType = computed<SliceType>(() => {
        if (!calendarAverageEnabled.value) return "full";
        if (
            granularity.value === "year" &&
            calendarSelectedMonth.value !== null
        )
            return "month_of_year";
        if (granularity.value === "month" && calendarSelectedDay.value !== null)
            return "day_of_month";
        return "full";
    });

    const isCalendarHeatmap = computed(() => {
        if (chartType.value !== "calendar") return false;
        if (granularity.value === "day") return false;
        if (!calendarAverageEnabled.value) return false;
        if (granularity.value === "year")
            return calendarSelectedMonth.value === null;
        return calendarSelectedDay.value === null;
    });

    const selectedStationsAndNational = computed<DeviationStationIdAndName[]>(
        () => {
            const stations = selectedStations.value.map((station) => {
                return {
                    station_id: station.code,
                    station_name: `${station.nom} (${station.departement})`,
                    departement: String(station.departement),
                };
            });

            return includeNational.value
                ? [
                      {
                          station_id: "national",
                          station_name: "France Métropolitaine",
                          departement: "",
                      },
                      ...stations,
                  ]
                : stations;
        },
    );

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

    const params = computed<TemperatureDeviationGraphParams>(() => ({
        date_start: dateToStringYMD(effectiveDateStart.value),
        date_end: dateToStringYMD(effectiveDateEnd.value),
        granularity:
            chartType.value === "calendar"
                ? calendarEffectiveGranularity.value
                : granularity.value,
        station_ids: stationIds.value.join(","),
        include_national: includeNational.value,
        slice_type:
            chartType.value === "calendar"
                ? calendarEffectiveSliceType.value
                : sliceType.value,
        month_of_year:
            chartType.value === "calendar"
                ? calendarEffectiveSliceType.value === "month_of_year"
                    ? calendarSelectedMonth.value!
                    : undefined
                : month_of_year.value,
        day_of_month:
            chartType.value === "calendar"
                ? calendarEffectiveSliceType.value === "day_of_month"
                    ? calendarSelectedDay.value!
                    : undefined
                : day_of_month.value,
    }));

    const {
        data: deviationData,
        pending,
        error,
    } = useTemperatureDeviationGraph(params);

    const setGranularity = (value: GranularityType) => {
        sliceType.value = "full";
        granularity.value = value;
        pickedDateEnd.value = dates.yesterday.value;
        maxDate.value = dates.yesterday.value;
        calendarAverageEnabled.value = false;
        calendarSliceMode.value = "all";
        if (value === "day") {
            sliceTypeSwitchEnabled.value = false;
            pickedDateStart.value = dates.lastYear.value;
        }
        if (value === "month") {
            pickedDateStart.value = dates.last10Year.value;
            pickedDateEnd.value = dates.lastMonth.value;
        }
        if (value === "year") {
            pickedDateStart.value = dates.absoluteMinDataDate.value;
            pickedDateEnd.value = dates.lastYear.value;
        }
    };

    const turnOffSliceType = (value: boolean) => {
        if (!value) {
            sliceType.value = "full";
        }
    };

    const setChartType = (value: ChartType) => {
        chartType.value = value;
        calendarAverageEnabled.value = false;
        calendarSliceMode.value = "all";
    };

    const setCalendarAverageEnabled = (value: boolean) => {
        if (!value) {
            calendarSliceMode.value = "all";
        }
    };

    const setStations = (stations: Station[]) => {
        stationIds.value = stations.map((station) => station.code);
        selectedStations.value = stations;
    };

    const setIncludeNational = (value: boolean) => {
        includeNational.value = value;
    };

    const stationsAndNationalFormatted = (
        chartData: TemperatureDeviationGraphResponse,
    ): TemperatureDeviationGraphStationSerie[] => {
        return includeNational.value
            ? [
                  {
                      station_id: "national",
                      station_name: "France Métropolitaine",
                      departement: "75",
                      ...chartData.national,
                  },
                  ...chartData.stations,
              ]
            : chartData.stations;
    };

    return {
        deviationChartRef,
        includeNational,
        pickedDateStart,
        pickedDateEnd,
        maxDate,
        granularity,
        sliceTypeSwitchEnabled,
        sliceType,
        sliceDatepickerDate,
        chartTypeSwitchEnabled,
        chartType,
        calendarAverageEnabled,
        calendarSliceMode,
        calendarDatepickerDate,
        isCalendarHeatmap,
        setGranularity,
        turnOffSliceType,
        setIncludeNational,
        setChartType,
        setCalendarAverageEnabled,
        setStations,
        stationsAndNationalFormatted,
        stationIds,
        selectedStations,
        selectedStationsAndNational,
        effectiveDateStart,
        effectiveDateEnd,
        deviationData,
        pending,
        error,
    };
});
