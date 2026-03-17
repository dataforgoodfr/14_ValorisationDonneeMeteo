import { useCustomDate } from "#imports";
import { GetChartData, TimeAxisType } from "~~/public/ChartDataProvider"; // provide init-options

const dates = useCustomDate();

export const useDeviationStore = defineStore("deviationStore", () => {
    const chartRef = shallowRef();
    const picked_date_start = ref(dates.lastYear.value);
    const picked_date_end = ref(dates.twoDaysAgo.value);
    const granularity = ref("month" as "year" | "month" | "day");
    const station_ids = ref<undefined | string[]>(undefined);
    const include_national = ref<boolean>(true);

    // ---------------- /!\ To remplace when API point "/temperature/deviation" is operational  /!\  ----------------
    const data = GetChartData(TimeAxisType.Day);
    // import type { DeviationParams } from "~/types/api";
    //     const params = computed<DeviationParams>(() => ({
    //     date_start: picked_date_start.value.toISOString().substring(0, 10),
    //     date_end: picked_date_end.value.toISOString().substring(0, 10),
    //     granularity: granularity.value,
    //     station_ids: station_ids.value,
    //     include_national: include_national.value,
    // }));
    // const {
    //     data: data,
    //     pending,
    //     error,
    // } = useTemperatureDeviation(params);
    // ---------------------------------------------------------------------------------------------------------------

    return {
        chartRef,
        picked_date_start,
        picked_date_end,
        granularity,
        station_ids,
        include_national,
        data,
    };
});
