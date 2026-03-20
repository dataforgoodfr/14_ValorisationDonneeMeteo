<script setup lang="ts">
import { refDebounced, useIntersectionObserver } from "@vueuse/core";
import type { PaginatedResponse, Station } from "~/types/api";

interface Props {
    selectedStations: Station[];
    onSelect: (station: Station) => void;
    onUnselect: (station: Station) => void;
}
const props = defineProps<Props>();

const { useApiFetch } = useApiClient();

const searchQuery = ref("");
const page = ref(1);
const allStations = ref<Station[]>([]);
const hasMore = ref(false);

const { data: stationsData, refresh } = await useApiFetch<
    PaginatedResponse<Station>
>("/stations", {
    query: {
        search: searchQuery,
    },
    immediate: true,
});

function processStations(newData: PaginatedResponse<Station> | undefined) {
    if (!newData) return;
    if (page.value === 1) {
        allStations.value = newData.results;
    } else {
        allStations.value = [...allStations.value, ...newData.results];
    }
    hasMore.value = !!newData.next;
}

watch(stationsData, processStations);
processStations(stationsData.value);

function onSelectStation(_event: Event, station: Station) {
    props.onSelect(station);
}

function onUnselectStation(_event: Event, station: Station) {
    props.onUnselect(station);
}

const filteredStations = computed(() =>
    allStations.value?.filter((station) =>
        props.selectedStations.length > 0
            ? !props.selectedStations.some((s) => s.code === station.code)
            : true,
    ),
);

const debouncedSearch = refDebounced(searchQuery, 300);

watch(debouncedSearch, () => {
    page.value = 1;
    refresh();
});

const sentinel = ref<HTMLElement | undefined>(undefined);

function loadMore() {
    if (!hasMore.value) return;
    page.value++;
    refresh();
}

useIntersectionObserver(sentinel, ([entry]) => {
    if (entry?.isIntersecting) loadMore();
});
</script>
<template>
    <UInput
        v-model="searchQuery"
        trailing-icon="i-lucide-search"
        size="md"
        variant="outline"
        placeholder="Entrez le nom d'une station"
    />

    <ul>
        <li
            v-for="(station, index) in props.selectedStations"
            :key="index"
            class="cursor-pointer pr-2 font-bold py-1 text-sm flex items-center justify-between"
            @click="onUnselectStation($event, station)"
        >
            <span class="truncate"
                >{{ station.nom }} ({{ station.departement }})</span
            >
            <UIcon name="i-lucide-x" class="shrink-0" />
        </li>
    </ul>
    <USeparator v-if="props.selectedStations.length > 0" />

    <div class="max-h-64 overflow-y-auto">
        <ul>
            <li
                v-for="(station, index) in filteredStations"
                :key="index"
                :title="`${station.nom} (${station.departement})`"
                class="cursor-pointer pr-2 py-1 text-sm flex items-center justify-between"
                @click="onSelectStation($event, station)"
            >
                <span class="truncate"
                    >{{ station.nom }} ({{ station.departement }})</span
                >
                <UIcon name="i-lucide-plus" class="shrink-0" />
            </li>
            <li ref="sentinel" class="py-1 text-center text-xs text-gray-400">
                <span v-if="hasMore">Chargement...</span>
            </li>
        </ul>
    </div>
</template>
