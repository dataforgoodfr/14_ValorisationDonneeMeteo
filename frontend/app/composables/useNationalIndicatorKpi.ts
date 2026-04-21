import type {
    NationalIndicatorKpiParams,
    NationalIndicatorKpiResponse,
} from "~/types/api";

export function useNationalIndicatorKpi(
    params: MaybeRef<NationalIndicatorKpiParams>,
) {
    const { useApiFetch } = useApiClient();

    return useApiFetch<NationalIndicatorKpiResponse>(
        "/temperature/national-indicator/kpi",
        { query: params },
    );
}
