import type {
    NationalIndicatorKpiParams,
    NationalIndicatorKpiResponse,
} from "~/types/api";

export function useNationalIndicatorKpi(
    params: MaybeRef<NationalIndicatorKpiParams>,
    enabled?: MaybeRef<boolean>,
) {
    const { createWatchedQuery } = useApiClient();

    return createWatchedQuery<
        NationalIndicatorKpiResponse,
        NationalIndicatorKpiParams
    >("/temperature/national-indicator/kpi", params, enabled);
}
