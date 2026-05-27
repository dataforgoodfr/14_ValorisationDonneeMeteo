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

    function createWatchedQuery<T, P>(
        endpoint: string,
        params: MaybeRef<P>,
        enabled?: MaybeRef<boolean>,
    ) {
        const isEnabled = computed<boolean>(() =>
            enabled !== undefined ? toValue(enabled) : true,
        );

        const result = useApiFetch<T>(endpoint, {
            query: computed(() => toValue(params)),
            immediate: false,
            watch: false,
            server: false,
            key: `${toValue(endpoint)}-${Math.random()}`, // Bypass useFetch cache sharing between pages
        });

        watch(
            [isEnabled, params],
            ([enabled]) => {
                if (import.meta.client && enabled) {
                    result.execute();
                }
            },
            { immediate: true },
        );

        return result;
    }

    return { apiFetch, useApiFetch, createWatchedQuery, baseURL };
}
