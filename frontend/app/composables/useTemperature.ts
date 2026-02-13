/**
 * Composables for planned temperature endpoints.
 * These endpoints are not yet implemented in the backend.
 * Parameter types will be narrowed when the OpenAPI spec is finalized.
 */

export function useTemperatureDeviation(params?: MaybeRef<Record<string, unknown>>) {
  const { useApiFetch } = useApiClient()
  return useApiFetch('/temperature/deviation', { query: params })
}

export function useTemperatureExtremes(params?: MaybeRef<Record<string, unknown>>) {
  const { useApiFetch } = useApiClient()
  return useApiFetch('/temperature/extremes', { query: params })
}

export function useTemperatureRecords(params?: MaybeRef<Record<string, unknown>>) {
  const { useApiFetch } = useApiClient()
  return useApiFetch('/temperature/records', { query: params })
}

export function useCumulativeRecords(params?: MaybeRef<Record<string, unknown>>) {
  const { useApiFetch } = useApiClient()
  return useApiFetch('/temperature/records/cumulative', { query: params })
}
