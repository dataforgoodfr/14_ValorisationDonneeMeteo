import type {
  HourlyMeasurement,
  HourlyDataFilters,
  PaginatedResponse,
} from '~/types/api'

export function useHourlyData(filters?: MaybeRef<HourlyDataFilters>) {
  const { useApiFetch } = useApiClient()

  return useApiFetch<PaginatedResponse<HourlyMeasurement>>(
    '/horaire/',
    {
      query: filters,
    },
  )
}

export function useLatestMeasurements() {
  const { useApiFetch } = useApiClient()

  return useApiFetch<HourlyMeasurement[]>('/horaire/latest/')
}
