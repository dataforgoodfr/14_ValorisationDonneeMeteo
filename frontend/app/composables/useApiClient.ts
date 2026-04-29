export function useApiClient() {
    const config = useRuntimeConfig();
    const baseURL = config.public.apiBase;

    function apiFetch<T>(
        endpoint: string,
        options?: Parameters<typeof $fetch<T>>[1],
    ): Promise<T> {
        return $fetch<T>(endpoint, {
            baseURL,
            ...options,
        });
    }

    function useApiFetch<T>(
        endpoint: string | Ref<string> | (() => string),
        options?: Parameters<typeof useFetch<T>>[1],
    ) {
        return useFetch<T>(endpoint, {
            baseURL,
            ...options,
        });
    }

    function useApiQuery<T, P>(
        endpoint: string,
        params: MaybeRef<P>,
        enabled?: MaybeRef<boolean>,
    ) {
        const isEnabled = computed<boolean>(() =>
            enabled !== undefined ? toValue(enabled) : true,
        );

        const result = useApiFetch<T>(endpoint, {
            query: params,
            immediate: false,
            watch: false,
        });

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

    return { apiFetch, useApiFetch, useApiQuery, baseURL };
}
