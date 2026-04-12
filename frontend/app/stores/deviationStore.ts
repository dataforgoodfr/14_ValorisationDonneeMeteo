import type {
    DeviationParams,
    DeviationResponse,
    DeviationStationSerie,
    Station,
} from "~/types/api";
import {
    useCustomDate,
    dateToFirstDayOfYearYMD,
    dateToLastDayOfYearYMD,
} from "#imports";
import type {
    GranularityType,
    SliceType,
    ChartType,
} from "~/components/ui/commons/selectBar/types";
import type { DeviationStationIdAndName } from "~/types/common";

const dates = useCustomDate();

export const useDeviationStore = defineStore("deviationStore", () => {
    const deviationChartRef = shallowRef();

    const pickedDateStart = ref(dates.lastYear.value);
    const pickedDateEnd = ref(dates.twoDaysAgo.value);

    const granularity: Ref<GranularityType> = ref<GranularityType>("month");
    const sliceTypeSwitchEnabled = ref(false);
    const sliceType: Ref<SliceType> = ref<SliceType>("full");

    const sliceDatepickerDate = ref(new Date(2006, 0, 1));

    const chartTypeSwitchEnabled = ref(false);
    const chartType: Ref<ChartType> = ref<ChartType>(`bar`);

    const stationIds = ref<string[]>([]);
    const selectedStations = ref<Station[]>([]);
    const includeNational = ref<boolean>(true);

    const isGranularityYear = computed<boolean>(
        () => granularity.value === "year",
    );

    const params = computed<DeviationParams>(() => {
        return {
            date_start: rangeDatesByGranularity.value.date_start,
            date_end: rangeDatesByGranularity.value.date_end,
            granularity:
                chartType.value === "calendar"
                    ? granularity.value === "month"
                        ? "day"
                        : "month" // gère l'exception du calendrier pour granularité
                    : granularity.value,
            station_ids: stationIds.value.join(","),
            include_national: includeNational.value,
        };
    });

    const rangeDatesByGranularity = computed<{
        date_start: string;
        date_end: string;
    }>(() => {
        return {
            date_start: isGranularityYear.value
                ? dateToFirstDayOfYearYMD(pickedDateStart.value)
                : dateToStringYMD(pickedDateStart.value),
            date_end: isGranularityYear.value
                ? dateToLastDayOfYearYMD(pickedDateEnd.value)
                : dateToStringYMD(pickedDateEnd.value),
        };
    });

    const selectedStationsAndNational = computed<DeviationStationIdAndName[]>(
        () => {
            const stations = selectedStations.value.map((station) => {
                return {
                    station_id: station.code,
                    station_name: `${station.nom} (${station.departement})`,
                };
            });

            return includeNational.value
                ? [
                      {
                          station_id: "national",
                          station_name: "France Métropolitaine",
                      },
                      ...stations,
                  ]
                : stations;
        },
    );

    const {
        data: deviationData,
        pending,
        error,
    } = useTemperatureDeviation(params);

    const setGranularity = (value: GranularityType) => {
        sliceType.value = "full";
        granularity.value = value;
        if (value === "day") {
            sliceTypeSwitchEnabled.value = false;
        }
    };

    const setChartType = (value: ChartType) => {
        chartType.value = value;
    };

    const setStations = (stations: Station[]) => {
        stationIds.value = stations.map((station) => station.code);
        selectedStations.value = stations;
    };

    const setIncludeNational = (value: boolean) => {
        includeNational.value = value;
    };

    const stationsAndNationalFormatted = (
        chartData: DeviationResponse,
    ): DeviationStationSerie[] => {
        return includeNational.value
            ? [
                  {
                      station_id: "national",
                      station_name: "France Métropolitaine",
                      ...chartData.national,
                  },
                  ...chartData.stations,
              ]
            : chartData.stations;
    };

    watch(isGranularityYear, (value) => {
        if (value) {
            pickedDateStart.value = new Date(
                dateToFirstDayOfYearYMD(pickedDateStart.value),
            );
            pickedDateEnd.value = new Date(
                dateToLastDayOfYearYMD(pickedDateEnd.value),
            );
        }
    });

    return {
        deviationChartRef,
        includeNational,
        pickedDateStart,
        pickedDateEnd,
        granularity,
        sliceTypeSwitchEnabled,
        sliceType,
        sliceDatepickerDate,
        chartTypeSwitchEnabled,
        chartType,
        setGranularity,
        setIncludeNational,
        setChartType,
        setStations,
        stationsAndNationalFormatted,
        stationIds,
        selectedStations,
        selectedStationsAndNational,
        deviationData,
        pending,
        error,
    };
});
