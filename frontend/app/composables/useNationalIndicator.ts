import type {
    NationalIndicatorParams,
    NationalIndicatorResponse,
} from "~/types/api";

export function useNationalIndicator(
    params: MaybeRef<NationalIndicatorParams>,
    enabled?: MaybeRef<boolean>,
) {
    const { createWatchedQuery } = useApiClient();

    return createWatchedQuery<
        NationalIndicatorResponse,
        NationalIndicatorParams
    >("/temperature/national-indicator", params, enabled);
}
