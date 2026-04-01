<script setup lang="ts">
import { useIntersectionObserver } from "@vueuse/core";
import type { Station } from "~/types/api";

const props = defineProps(["searchQuery"]);
const store = useRecordsGraphStore();
const { stationNameFilter } = storeToRefs(store);
const { setStationFilter } = store;

const searchQueryRef = toRef(props, "searchQuery");

const params = computed(() => ({
    search: searchQueryRef.value,
}));

const { allStations, onRefresh, hasMore } =
    useStationsWithInfiniteScroll(params);

function onSelectStation(_event: PointerEvent, station: Station) {
    setStationFilter(station);
}

const unselectedFilteredStations = computed(() => {
    const stationNamesFilter = stationNameFilter.value;
    return allStations.value.filter((s) => !stationNamesFilter.includes(s.nom));
});

const sentinel = ref<HTMLElement | undefined>(undefined);

function loadMore() {
    if (!hasMore.value) return;
    onRefresh();
}

useIntersectionObserver(sentinel, ([entry]) => {
    if (entry?.isIntersecting) loadMore();
});
</script>
<template>
    <div class="overflow-y-auto">
        <ul>
            <li
                v-for="station in unselectedFilteredStations"
                :key="`filtered-${station.nom}`"
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
</template>
