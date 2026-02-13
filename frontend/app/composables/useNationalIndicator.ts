import type {
    NationalIndicatorParams,
    NationalIndicatorResponse,
} from "~/types/api";

export function useNationalIndicator(
    params: MaybeRef<NationalIndicatorParams>,
) {
    const { useApiFetch } = useApiClient();

    return useApiFetch<NationalIndicatorResponse>(
        "/temperature/national-indicator",
        {
            query: params,
        },
    );
}
