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

    return { apiFetch, useApiFetch, baseURL };
}
