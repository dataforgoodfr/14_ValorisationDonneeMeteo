<script setup lang="ts">
import { refDebounced, useIntersectionObserver } from "@vueuse/core";
import type { Station } from "~/types/api";

const deviationStore = useDeviationStore();
const { includeNational, selectedStations } = storeToRefs(deviationStore);

const searchQuery = ref<undefined | string>(undefined);
const debouncedSearch = refDebounced(searchQuery, 300);

const params = computed(() => ({
    search: debouncedSearch.value,
}));
const { allStations, onLoadMore, hasMore } =
    useStationsWithInfiniteScroll(params);

function onSelectStation(_event: PointerEvent, station: Station) {
    deviationStore.setStations([...deviationStore.selectedStations, station]);
}

function onUnselectStation(_event: PointerEvent, station: Station) {
    if (!deviationStore.setStations) return;
    deviationStore.setStations(
        deviationStore.selectedStations.filter((s) => s.code !== station.code),
    );
}

const isStationSelected = (station: Station) =>
    selectedStations.value.some((s) => s.code === station.code);

const unselectedFilteredStations = computed(() =>
    selectedStations.value.length === 0
        ? allStations.value
        : allStations.value.filter((s) => !isStationSelected(s)),
);

const sentinel = ref<HTMLElement | undefined>(undefined);

function loadMore() {
    if (!hasMore.value) return;
    onLoadMore();
}

useIntersectionObserver(sentinel, ([entry]) => {
    if (entry?.isIntersecting) loadMore();
});
</script>
<template>
    <div class="flex flex-col gap-2 w-64 p-4 h-full max-h-158">
        <UInput
            v-model="searchQuery"
            trailing-icon="i-lucide-search"
            size="md"
            variant="outline"
            placeholder="Entrez le nom d'une station"
        />
        <div
            v-if="selectedStations.length > 0 || includeNational"
            class="max-h-44 overflow-y-auto shrink-0"
        >
            <ul>
                <li
                    v-if="includeNational"
                    class="cursor-pointer pr-2 font-bold py-1 text-sm flex items-center justify-between"
                    :title="'France Métropolitaine'"
                    @click="deviationStore.setIncludeNational(false)"
                >
                    <span>France Métropolitaine</span>
                    <UIcon :name="'i-lucide-x'" class="shrink-0" />
                </li>
                <li
                    v-for="station in selectedStations"
                    :key="`selected-${station.code}`"
                    :title="`${station.nom} (${station.departement})`"
                    class="cursor-pointer pr-2 font-bold py-1 text-sm flex items-center justify-between"
                    @click="onUnselectStation($event, station)"
                >
                    <span class="truncate"
                        >{{ station.nom }} ({{ station.departement }})</span
                    >
                    <UIcon name="i-lucide-x" class="shrink-0" />
                </li>
            </ul>
        </div>

        <USeparator v-if="selectedStations.length > 0 || includeNational" />

        <div class="overflow-y-auto">
            <ul>
                <li
                    v-if="!includeNational"
                    class="cursor-pointer pr-2 py-1 text-sm flex items-center justify-between"
                    :title="'France Métropolitaine'"
                    @click="deviationStore.setIncludeNational(true)"
                >
                    <span>France Métropolitaine</span>
                    <UIcon :name="'i-lucide-plus'" class="shrink-0" />
                </li>
                <li
                    v-for="station in unselectedFilteredStations"
                    :key="`filtered-${station.code}`"
                    :title="`${station.nom} (${station.departement})`"
                    class="cursor-pointer pr-2 py-1 text-sm flex items-center justify-between"
                    @click="onSelectStation($event, station)"
                >
                    <span class="truncate"
                        >{{ station.nom }} ({{ station.departement }})</span
                    >
                    <UIcon name="i-lucide-plus" class="shrink-0" />
                </li>
                <li
                    v-if="hasMore"
                    ref="sentinel"
                    class="py-1 text-center text-xs text-gray-400"
                >
                    <span>Chargement...</span>
                </li>
            </ul>
        </div>
    </div>
</template>
