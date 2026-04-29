import type {
    NationalIndicatorKpiParams,
    NationalIndicatorKpiResponse,
} from "~/types/api";

export function useNationalIndicatorKpi(
    params: MaybeRef<NationalIndicatorKpiParams>,
    enabled?: MaybeRef<boolean>,
) {
    const { useApiQuery } = useApiClient();

    return useApiQuery<
        NationalIndicatorKpiResponse,
        NationalIndicatorKpiParams
    >("/temperature/national-indicator/kpi", params, enabled);
}
