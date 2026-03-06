import type { DeviationParams } from "~/types/api";
import { useCustomDate } from "#imports";

const dates = useCustomDate();

export const useDeviationStore = defineStore("DeviationStore", () => {
    const picked_date_start = ref(dates.lastYear.value);
    const picked_date_end = ref(dates.twoDaysAgo.value);
    const granularity = ref("month" as "year" | "month" | "day");
    const station_ids = ref<undefined | string[]>(undefined);
    const include_national = ref<boolean>(true);

    const params = computed<DeviationParams>(() => ({
        date_start: picked_date_start.value.toISOString().substring(0, 10),
        date_end: picked_date_end.value.toISOString().substring(0, 10),
        granularity: granularity.value,
        station_ids: station_ids.value,
        include_national: include_national.value,
    }));

    const {
        data: deviationData,
        pending,
        error,
    } = useTemperatureDeviation(params);

    return {
        picked_date_start,
        picked_date_end,
        granularity,
        station_ids,
        include_national,
        deviationData,
        pending,
        error,
    };
});
