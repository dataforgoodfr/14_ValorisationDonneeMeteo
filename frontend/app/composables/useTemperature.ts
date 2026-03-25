import type { DeviationParams, DeviationResponse } from "~/types/api";

export function useTemperatureDeviation(
    params: MaybeRef<DeviationParams>,
    enabled?: MaybeRef<boolean>,
) {
    const { useApiFetch } = useApiClient();

    if (enabled === undefined) {
        return useApiFetch<DeviationResponse>("/temperature/deviation", {
            query: params,
        });
    }

    const isEnabled = toRef(enabled);

    const result = useApiFetch<DeviationResponse>("/temperature/deviation", {
        query: params,
        imediate: isEnabled.value,
        watch: false,
    });

    watch([isEnabled, params], () => {
        if (isEnabled.value) {
            result.execute();
        }
    });

    return result;
}

export function useTemperatureExtremes(
    params?: MaybeRef<Record<string, unknown>>,
) {
    const { useApiFetch } = useApiClient();
    return useApiFetch("/temperature/extremes", { query: params });
}

export function useTemperatureRecords(
    params?: MaybeRef<Record<string, unknown>>,
) {
    const { useApiFetch } = useApiClient();
    return useApiFetch("/temperature/records", { query: params });
}

export function useCumulativeRecords(
    params?: MaybeRef<Record<string, unknown>>,
) {
    const { useApiFetch } = useApiClient();
    return useApiFetch("/temperature/records/cumulative", { query: params });
}
