import type { DeviationParams, Station } from "~/types/api";
import { useCustomDate } from "#imports";
import type {
    GranularityType,
    SliceType,
    ChartType,
} from "~/components/ui/commons/selectBar/types";

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

    const params = computed<DeviationParams>(() => ({
        date_start: pickedDateStart.value
            .toISOString()
            .substring(0, "YYYY-MM-DD".length),
        date_end: pickedDateEnd.value
            .toISOString()
            .substring(0, "YYYY-MM-DD".length),
        granularity: granularity.value,
        station_ids: stationIds.value.join(","),
        include_national: includeNational.value,
    }));

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

    return {
        deviationChartRef,
        pickedDateStart,
        pickedDateEnd,
        granularity,
        sliceTypeSwitchEnabled,
        sliceType,
        sliceDatepickerDate,
        chartTypeSwitchEnabled,
        chartType,
        setGranularity,
        setChartType,
        setStations,
        stationIds,
        selectedStations,
        includeNational,
        deviationData,
        pending,
        error,
    };
});
