<script setup lang="ts">
import { refDebounced } from "@vueuse/core";
import type { PaginatedResponse, Station } from "~/types/api";

const mockedStations: Station[] = [
    {
        id: 1,
        code: "ST001",
        nom: "Station Loire 1",
        departement: 44,
        frequence: "10min",
        poste_ouvert: true,
        type_poste: 1,
        lon: -1.5536,
        lat: 47.2184,
        alt: 12,
        poste_public: true,
    },
    {
        id: 2,
        code: "ST002",
        nom: "Station Loire 2",
        departement: 44,
        frequence: "10min",
        poste_ouvert: true,
        type_poste: 2,
        lon: -1.5401,
        lat: 47.2201,
        alt: 15,
        poste_public: false,
    },
    {
        id: 3,
        code: "ST003",
        nom: "Station Erdre 1",
        departement: 44,
        frequence: "30min",
        poste_ouvert: true,
        type_poste: 1,
        lon: -1.548,
        lat: 47.235,
        alt: 10,
        poste_public: true,
    },
    {
        id: 4,
        code: "ST004",
        nom: "Station Erdre 2",
        departement: 44,
        frequence: "30min",
        poste_ouvert: false,
        type_poste: 3,
        lon: -1.545,
        lat: 47.238,
        alt: 14,
        poste_public: false,
    },
    {
        id: 5,
        code: "ST005",
        nom: "Station Nantes Nord",
        departement: 44,
        frequence: "15min",
        poste_ouvert: true,
        type_poste: 2,
        lon: -1.57,
        lat: 47.245,
        alt: 18,
        poste_public: true,
    },
    {
        id: 6,
        code: "ST006",
        nom: "Station Nantes Sud",
        departement: 44,
        frequence: "15min",
        poste_ouvert: true,
        type_poste: 1,
        lon: -1.54,
        lat: 47.19,
        alt: 11,
        poste_public: true,
    },
    {
        id: 7,
        code: "ST007",
        nom: "Station Sèvre",
        departement: 44,
        frequence: "60min",
        poste_ouvert: true,
        type_poste: 3,
        lon: -1.51,
        lat: 47.17,
        alt: 20,
        poste_public: false,
    },
    {
        id: 8,
        code: "ST008",
        nom: "Station Vertou",
        departement: 44,
        frequence: "60min",
        poste_ouvert: true,
        type_poste: 2,
        lon: -1.48,
        lat: 47.17,
        alt: 16,
        poste_public: true,
    },
    {
        id: 9,
        code: "ST009",
        nom: "Station Rezé",
        departement: 44,
        frequence: "20min",
        poste_ouvert: true,
        type_poste: 1,
        lon: -1.55,
        lat: 47.19,
        alt: 13,
        poste_public: true,
    },
    {
        id: 10,
        code: "ST010",
        nom: "Station Saint-Herblain",
        departement: 44,
        frequence: "20min",
        poste_ouvert: false,
        type_poste: 2,
        lon: -1.6,
        lat: 47.21,
        alt: 19,
        poste_public: false,
    },

    {
        id: 11,
        code: "ST011",
        nom: "Station Atlantique 1",
        departement: 44,
        frequence: "10min",
        poste_ouvert: true,
        type_poste: 1,
        lon: -1.62,
        lat: 47.23,
        alt: 22,
        poste_public: true,
    },
    {
        id: 12,
        code: "ST012",
        nom: "Station Atlantique 2",
        departement: 44,
        frequence: "10min",
        poste_ouvert: true,
        type_poste: 3,
        lon: -1.63,
        lat: 47.24,
        alt: 24,
        poste_public: false,
    },
    {
        id: 13,
        code: "ST013",
        nom: "Station Atlantique 3",
        departement: 44,
        frequence: "20min",
        poste_ouvert: true,
        type_poste: 2,
        lon: -1.64,
        lat: 47.25,
        alt: 26,
        poste_public: true,
    },
    {
        id: 14,
        code: "ST014",
        nom: "Station Atlantique 4",
        departement: 44,
        frequence: "20min",
        poste_ouvert: false,
        type_poste: 2,
        lon: -1.65,
        lat: 47.26,
        alt: 28,
        poste_public: false,
    },
    {
        id: 15,
        code: "ST015",
        nom: "Station Atlantique 5",
        departement: 44,
        frequence: "30min",
        poste_ouvert: true,
        type_poste: 1,
        lon: -1.66,
        lat: 47.27,
        alt: 30,
        poste_public: true,
    },

    {
        id: 16,
        code: "ST016",
        nom: "Station Vendée 1",
        departement: 85,
        frequence: "60min",
        poste_ouvert: true,
        type_poste: 3,
        lon: -1.7,
        lat: 46.65,
        alt: 12,
        poste_public: true,
    },
    {
        id: 17,
        code: "ST017",
        nom: "Station Vendée 2",
        departement: 85,
        frequence: "60min",
        poste_ouvert: true,
        type_poste: 2,
        lon: -1.72,
        lat: 46.66,
        alt: 14,
        poste_public: false,
    },
    {
        id: 18,
        code: "ST018",
        nom: "Station Vendée 3",
        departement: 85,
        frequence: "30min",
        poste_ouvert: true,
        type_poste: 1,
        lon: -1.74,
        lat: 46.67,
        alt: 16,
        poste_public: true,
    },
    {
        id: 19,
        code: "ST019",
        nom: "Station Vendée 4",
        departement: 85,
        frequence: "30min",
        poste_ouvert: false,
        type_poste: 2,
        lon: -1.76,
        lat: 46.68,
        alt: 18,
        poste_public: false,
    },
    {
        id: 20,
        code: "ST020",
        nom: "Station Vendée 5",
        departement: 85,
        frequence: "15min",
        poste_ouvert: true,
        type_poste: 3,
        lon: -1.78,
        lat: 46.69,
        alt: 20,
        poste_public: true,
    },
];
const deviationStore = useDeviationStore();
const { station_ids } = storeToRefs(deviationStore);
console.log("1 - Selected station IDs from store:", station_ids.value);
const { useApiFetch } = useApiClient();

const searchQuery = ref("");
const page = ref(1);

const {
    data: stations,
    pending: loading,
    error,
    refresh,
} = await useApiFetch<PaginatedResponse<Station>>("/stations", {
    query: {
        search: searchQuery,
    },
    watch: [searchQuery],
});

function onSelectStation(_event: Event, stationId: number) {
    if (station_ids.value && station_ids.value.length > 0) {
        deviationStore.setStationIds([...station_ids.value, stationId]);
    } else {
        deviationStore.setStationIds([stationId]);
    }
}

function onUnselectStation(_event: Event, stationId: number) {
    if (!deviationStore.setStationIds) return;
    deviationStore.setStationIds(
        station_ids.value?.filter((id) => id !== stationId),
    );
}

const debouncedSearch = refDebounced(searchQuery, 300);

watch(debouncedSearch, () => {
    refresh();
});

// TODO: replace  mockedStations by  stations?.results when API is ready
const filteredStations = computed(() =>
    mockedStations.filter((station) =>
        station_ids.value
            ? !station_ids.value.some((id) => id === station.id)
            : true,
    ),
);

const paginatedStations = computed(() => {
    const start = (page.value - 1) * 10;
    const end = start + 10;
    return filteredStations.value.slice(start, end);
});

const totalPages = computed(() => Math.floor(filteredStations.value.length));
</script>
<template>
    <UInput
        v-model="searchQuery"
        trailing-icon="i-lucide-search"
        size="md"
        variant="outline"
        placeholder="Entrez le nom d'une station ou dept"
    />
    <ul>
        <li
            v-for="(stationId, index) in station_ids"
            :key="index"
            class="cursor-pointer font-bold py-1 text-sm flex items-center justify-between"
            @click="onUnselectStation($event, stationId)"
        >
            {{ mockedStations.find((s) => s.id === stationId)?.nom }} ({{
                mockedStations.find((s) => s.id === stationId)?.departement
            }})
            <UIcon name="i-lucide-x" />
        </li>
    </ul>
    <USeparator />
    <div>
        <ul>
            <li
                v-for="(station, index) in paginatedStations"
                :key="index"
                class="cursor-pointer py-1 text-sm flex items-center justify-between"
                @click="onSelectStation($event, station.id)"
            >
                {{ station.nom }} ({{ station.departement }})
                <UIcon name="i-lucide-plus" />
            </li>
            <UPagination
                v-model:page="page"
                class="p-2"
                :show-edges="totalPages > 5"
                :sibling-count="totalPages > 5 ? 1 : 0"
                :total="totalPages"
            />
        </ul>
    </div>
</template>
