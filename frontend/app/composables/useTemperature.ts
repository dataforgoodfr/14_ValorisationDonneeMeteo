import type {
    DeviationMapResponse,
    TemperatureRecordsGraphParams,
    TemperatureRecordsGraphResponse,
    TemperatureDeviationGraphParams,
    TemperatureDeviationGraphResponse,
    TemperatureDeviationParams,
    TemperatureDeviationResponse,
    TemperatureRecordsParams,
    TemperatureRecordsPaginatedResponse,
} from "~/types/api";

export function useTemperatureDeviation(
    params: MaybeRef<TemperatureDeviationParams>,
    enabled?: MaybeRef<boolean>,
    requireStations: boolean = true,
    key?: string,
) {
    const { useApiFetch } = useApiClient();

    const hasRequiredParams = computed(() => {
        const resolved = toValue(params);
        if (!requireStations) {
            return (
                resolved.date_start !== undefined &&
                resolved.date_end !== undefined
            );
        }
        return (
            resolved.station_ids !== undefined && resolved.station_ids !== ""
        );
    });

    const isEnabled = computed(() => toValue(enabled) ?? true);

    const result = useApiFetch<TemperatureDeviationResponse>(
        "/temperature/deviation",
        {
            query: params,
            immediate: false,
            watch: false,
            ...(key ? { key } : {}),
        },
    );

    watch(
        [isEnabled, hasRequiredParams, params],
        ([enabled, hasParams]) => {
            if (enabled && hasParams) {
                result.execute();
            } else if (!hasParams) {
                result.clear();
            }
        },
        { immediate: true, deep: true },
    );

    return result;
}

export function useTemperatureDeviationGraph(
    params: MaybeRef<TemperatureDeviationGraphParams>,
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

    const isEnabled = computed(() => toValue(enabled) ?? true);

    const result = useApiFetch<TemperatureDeviationGraphResponse>(
        "/temperature/deviation/graph",
        {
            query: params,
            immediate: false,
            watch: false,
        },
    );

    watch(
        [isEnabled, hasRequiredParams, params],
        ([enabled, hasParams]) => {
            if (enabled && hasParams) {
                result.execute();
            } else if (!hasParams) {
                result.clear();
            }
        },
        { immediate: true },
    );

    return result;
}

export function useTemperatureRecordsGraph(
    params: MaybeRef<TemperatureRecordsGraphParams>,
    enabled?: MaybeRef<boolean>,
) {
    const { useApiFetch } = useApiClient();

    const isEnabled = computed(() => toValue(enabled) ?? true);

    const result = useApiFetch<TemperatureRecordsGraphResponse>(
        "/temperature/records/graph",
        {
            query: params,
            immediate: false,
            watch: false,
        },
    );

    watch(
        [isEnabled, params],
        ([enabled]) => {
            if (enabled) {
                result.execute();
            }
        },
        { immediate: true },
    );

    return result;
}

export function useTemperatureAbsoluteRecordsGraph(
    params: MaybeRef<TemperatureRecordsGraphParams>,
    enabled?: MaybeRef<boolean>,
) {
    const { useApiFetch } = useApiClient();

    const isEnabled = computed(() => toValue(enabled) ?? true);

    const result = useApiFetch<TemperatureRecordsGraphResponse>(
        "/temperature/records/absolute/graph",
        {
            query: params,
            immediate: false,
            watch: false,
        },
    );

    watch(
        [isEnabled, params],
        ([enabled]) => {
            if (enabled) {
                result.execute();
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
    params: MaybeRef<TemperatureRecordsParams>,
) {
    const { useApiFetch } = useApiClient();

    return useApiFetch<TemperatureRecordsPaginatedResponse>(
        "/temperature/records",
        {
            query: params,
            server: false,
        },
    );
}

export function useTemperatureAbsoluteRecords(
    params: MaybeRef<TemperatureRecordsParams>,
) {
    const { useApiFetch } = useApiClient();

    return useApiFetch<TemperatureRecordsPaginatedResponse>(
        "/temperature/records/absolute",
        {
            query: params,
            server: false,
        },
    );
}

export function useCumulativeRecords(
    params?: MaybeRef<Record<string, unknown>>,
) {
    const { useApiFetch } = useApiClient();
    return useApiFetch("/temperature/records/cumulative", { query: params });
}

export function useTemperatureDeviationMap(
    params: MaybeRef<TemperatureDeviationParams>,
    key?: string,
) {
    const { useApiFetch } = useApiClient();
    return useApiFetch<DeviationMapResponse>("/temperature/deviation", {
        query: params,
        immediate: false,
        watch: false,
        ...(key ? { key } : {}),
    });
}
