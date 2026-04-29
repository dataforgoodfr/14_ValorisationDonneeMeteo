import type {
    NationalIndicatorParams,
    NationalIndicatorResponse,
} from "~/types/api";

export function useNationalIndicator(
    params: MaybeRef<NationalIndicatorParams>,
    enabled?: MaybeRef<boolean>,
) {
    const { useApiQuery } = useApiClient();

    return useApiQuery<NationalIndicatorResponse, NationalIndicatorParams>(
        "/temperature/national-indicator",
        params,
        enabled,
    );
}
