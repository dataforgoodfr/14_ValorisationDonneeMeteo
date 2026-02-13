export function useApiClient() {
    const config = useRuntimeConfig();
    const baseURL = config.public.apiBase as string;

    function apiFetch<T>(
        endpoint: string,
        options?: Record<string, unknown>,
    ): Promise<T> {
        return $fetch<T>(endpoint, {
            baseURL,
            ...options,
        });
    }

    function useApiFetch<T>(
        endpoint: string | Ref<string> | (() => string),
        options?: Record<string, unknown>,
    ) {
        return useFetch<T>(endpoint, {
            baseURL,
            ...options,
        });
    }

    return { apiFetch, useApiFetch, baseURL };
}
