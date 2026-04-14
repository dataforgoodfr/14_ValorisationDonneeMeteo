import type {
    TemperatureDeviationGraphParams,
    Station,
    TemperatureDeviationGraphResponse,
    TemperatureDeviationGraphStationSerie,
} from "~/types/api";
import { useCustomDate, dateToStringYMD } from "#imports";
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

    const params = computed<TemperatureDeviationGraphParams>(() => ({
        date_start: dateToStringYMD(pickedDateStart.value),
        date_end: dateToStringYMD(pickedDateEnd.value),
        granularity:
            chartType.value === "calendar"
                ? granularity.value === "month"
                    ? "day" // calendrier mois → données journalières (y-axis = jours)
                    : "month" // calendrier année → données mensuelles (y-axis = mois)
                : granularity.value,
        station_ids: stationIds.value.join(","),
        include_national: includeNational.value,
    }));

    const {
        data: deviationData,
        pending,
        error,
    } = useTemperatureDeviationGraph(params);

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

    watch(isGranularityYear, (value) => {
        if (value) {
            pickedDateStart.value = setToFirstDayOfYear(pickedDateStart.value);
            pickedDateEnd.value = setToLastDayOfYear(pickedDateEnd.value);
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
