<script setup lang="ts">
import type { TableColumn } from "@nuxt/ui";
import type { PaginatedResponse, Station } from "~/types/api";
import { refDebounced } from "@vueuse/core";

const { useApiFetch } = useApiClient();

// Search query for filtering
const searchQuery = ref("");
const selectedStation = ref<Station | null>(null);

// Fetch stations from API with search parameter
const {
    data: stations,
    pending: loading,
    error,
    refresh,
} = await useApiFetch<PaginatedResponse<Station>>("/stations", {
    query: {
        search: searchQuery,
    },
    // Watch the search query and refetch when it changes
    watch: [searchQuery],
});

// Define table columns
const columns: TableColumn<Station>[] = [
    {
        accessorKey: "code",
        header: "Code Station",
    },
    {
        accessorKey: "nom",
        header: "Nom de Station",
    },
    {
        accessorKey: "departement",
        header: "Département",
    },
    {
        accessorKey: "frequence",
        header: "Fréquence",
    },
    {
        accessorKey: "poste_ouvert",
        header: "Poste ouvert",
        cell: ({ row }) => (row.getValue("poste_ouvert") ? "Ouvert" : "Fermé"),
    },
    {
        id: "coordinates",
        header: "Coordonnées DD",
        cell: ({ row }) => `LON: ${row.original.lon} LAT: ${row.original.lat}`,
    },
    {
        accessorKey: "type_poste",
        header: "Type de poste",
    },
    {
        accessorKey: "poste_public",
        header: "Poste public",
        cell: ({ row }) => (row.getValue("poste_public") ? "Public" : "Non"),
    },
];

// Get table reference to access the API
const table = useTemplateRef("table");

// Handle row selection to update graph
function onSelectStation(_event: Event, _row: unknown) {
    // selectedStation.value = row.original;
    // Update your graph here with selectedStation.value
    console.log("Selected station:", selectedStation.value);
}

// Debounce the search query to avoid too many API calls
const debouncedSearch = refDebounced(searchQuery, 300);

// Watch debounced search and trigger refresh
watch(debouncedSearch, () => {
    refresh();
});
</script>

<template>
    <div class="flex flex-col gap-4">
        <!-- Search Input -->
        <div class="px-4 py-3.5 border-b border-accented">
            <UInput
                v-model="searchQuery"
                icon="i-lucide-search"
                placeholder="Search stations..."
                class="max-w-sm"
            />
        </div>

        <!-- Error message -->
        <div v-if="error" class="px-4 py-3 bg-error/10 text-error rounded">
            Error loading stations: {{ error.message }}
        </div>

        <!-- Table with clickable rows -->
        <UTable
            ref="table"
            :data="stations?.results || []"
            :columns="columns"
            :loading="loading"
            class="flex-1"
            @select="onSelectStation"
        />

        <!-- Graph component -->
        <div v-if="selectedStation" class="p-4 border border-accented rounded">
            <h3 class="font-semibold mb-2">
                Graph for {{ selectedStation.name }}
            </h3>
            <!-- Your graph component here -->
            <!-- <YourGraphComponent :station="selectedStation" /> -->
        </div>
    </div>
</template>
