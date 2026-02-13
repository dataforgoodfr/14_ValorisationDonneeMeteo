import type {
  Station,
  StationDetail,
  StationFilters,
  PaginatedResponse,
} from '~/types/api'

export function useStations(filters?: MaybeRef<StationFilters>) {
  const { useApiFetch } = useApiClient()

  return useApiFetch<PaginatedResponse<Station>>(
    '/stations/',
    {
      query: filters,
    },
  )
}

export function useStation(id: MaybeRef<number | string>) {
  const { useApiFetch } = useApiClient()

  return useApiFetch<StationDetail>(
    () => `/stations/${toValue(id)}/`,
  )
}
