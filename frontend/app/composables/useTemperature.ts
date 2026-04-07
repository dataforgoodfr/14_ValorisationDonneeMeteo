import type {
    DeviationParams,
    DeviationResponse,
    TemperatureRecordsParams,
    TemperatureRecordsResponse,
} from "~/types/api";

export function useTemperatureDeviation(
    params: MaybeRef<DeviationParams>,
    enabled?: MaybeRef<boolean>,
) {
    const { useApiFetch } = useApiClient();

    const hasRequiredParams = computed(() => {
        const resolved = toValue(params);
        return (
            resolved.include_national === true ||
            (resolved.station_ids !== undefined && resolved.station_ids !== "")
        );
    });

    const isEnabled = computed(() =>
        enabled !== undefined ? toValue(enabled) : true,
    );

    const result = useApiFetch<DeviationResponse>("/temperature/deviation", {
        query: params,
        immediate: false,
        watch: false,
    });

    watch(
        [isEnabled, hasRequiredParams, params],
        ([enabled, hasParams]) => {
            if (enabled && hasParams) {
                result.execute();
            } else if (!hasParams) {
                result.data.value = undefined;
            }
        },
        { immediate: true },
    );

    return result;
}

export function useTemperatureExtremes(
    params?: MaybeRef<Record<string, unknown>>,
) {
    const { useApiFetch } = useApiClient();
    return useApiFetch("/temperature/extremes", { query: params });
}

export function useTemperatureRecords(
    params?: MaybeRef<TemperatureRecordsParams>,
) {
    const { useApiFetch } = useApiClient();
    return useApiFetch<TemperatureRecordsResponse>("/temperature/records", {
        query: params,
    });
}

export function useCumulativeRecords(
    params?: MaybeRef<Record<string, unknown>>,
) {
    const { useApiFetch } = useApiClient();
    return useApiFetch("/temperature/records/cumulative", { query: params });
}
