import type { DeviationParams, Station } from "~/types/api";
import { useCustomDate } from "#imports";
import type {
    GranularityType,
    SliceType,
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

    const station_ids = ref<undefined | string[]>(undefined);
    const selected_stations = ref<Station[]>([]);
    const include_national = ref<boolean>(true);

    const params = computed<DeviationParams>(() => ({
        date_start: pickedDateStart.value.toISOString().substring(0, 10),
        date_end: pickedDateEnd.value.toISOString().substring(0, 10),
        granularity: granularity.value,
        station_ids: station_ids.value,
        include_national: include_national.value,
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

    const setStationIds = (ids: string[] | undefined) => {
        station_ids.value = ids;
    };

    const setStations = (stations: Station[] | undefined) => {
        station_ids.value = stations?.map((station) => station.code);
        selected_stations.value = stations || [];
    };

    return {
        deviationChartRef,
        pickedDateStart,
        pickedDateEnd,
        granularity,
        sliceTypeSwitchEnabled,
        sliceType,
        sliceDatepickerDate,
        setGranularity,
        setChartType,
        setStationIds,
        setStations,
        station_ids,
        selected_stations,
        include_national,
        deviationData,
        pending,
        error,
    };
});
