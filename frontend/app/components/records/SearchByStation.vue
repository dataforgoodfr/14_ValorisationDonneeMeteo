<script setup lang="ts">
import { refDebounced, useIntersectionObserver } from "@vueuse/core";
import { useStationsWithInfiniteScroll } from "~/composables/useStations";
import { useRecordsChartStore } from "#imports";
import type { Station } from "~/types/api";

const props = defineProps({
    searchQuery: {
        type: String,
        default: "",
    },
});
const store = useRecordsChartStore();
const { stationCodeFilter } = storeToRefs(store);
const { setStationFilter } = store;

const searchQueryRef = toRef(props, "searchQuery");
const debouncedSearch = refDebounced(searchQueryRef, 300);

const params = computed(() => ({
    search: debouncedSearch.value,
}));

const { allStations, onLoadMore, hasMore } =
    useStationsWithInfiniteScroll(params);

function onSelectStation(_event: PointerEvent, station: Station) {
    setStationFilter(station);
}

const unselectedFilteredStations = computed(() => {
    const stationCodesFilter = stationCodeFilter.value;
    return allStations.value.filter(
        (station) => !stationCodesFilter.includes(station.code),
    );
});

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
    <ClientOnly>
        <div class="overflow-y-auto">
            <ul>
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
    </ClientOnly>
</template>
