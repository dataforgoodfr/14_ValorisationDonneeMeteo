import type {
    NationalIndicatorParams,
    NationalIndicatorResponse,
} from "~/types/api";

export function useNationalIndicator(
    params: MaybeRef<NationalIndicatorParams>,
    enabled?: MaybeRef<boolean>,
) {
    const { useApiFetch } = useApiClient();

    if (enabled === undefined) {
        const result = useApiFetch<NationalIndicatorResponse>(
            "/temperature/national-indicator",
            { query: params, watch: false },
        );

        watch(params, () => {
            result.execute();
        });

        return result;
    }

    const isEnabled = toRef(enabled);

    const result = useApiFetch<NationalIndicatorResponse>(
        "/temperature/national-indicator",
        {
            query: params,
            immediate: isEnabled.value,
            watch: false,
        },
    );

    watch([isEnabled, params], () => {
        if (isEnabled.value) {
            result.execute();
        }
    });

    return result;
}
