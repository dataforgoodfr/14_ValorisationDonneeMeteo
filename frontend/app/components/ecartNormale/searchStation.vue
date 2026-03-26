<script setup lang="ts">
import { refDebounced, useIntersectionObserver } from "@vueuse/core";
import type { PaginatedResponse, Station } from "~/types/api";

const deviationStore = useDeviationStore();
const { selectedStations } = storeToRefs(deviationStore);

const searchQuery = ref<undefined | string>(undefined);
const page = ref<number>(0);
const allStations = ref<Station[]>([]);
const hasMore = ref<boolean>(false);

const params = computed(() => ({
    search: searchQuery.value,
    offset: page.value * 100,
}));
const { data: stationsData, refresh } = useStations(params);

function processStations(newData: PaginatedResponse<Station> | undefined) {
    if (!newData) return;
    if (page.value === 0) {
        allStations.value = newData.results;
    } else {
        allStations.value = [...allStations.value, ...newData.results];
    }
    hasMore.value = !!newData.next;
}

watch(stationsData, processStations);
onMounted(() => {
    processStations(stationsData.value);
});

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

const debouncedSearch = refDebounced(searchQuery, 300);
watch(debouncedSearch, () => {
    page.value = 0;
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
    <div class="flex flex-col gap-2 w-64 p-4 h-full max-h-158">
        <UInput
            v-model="searchQuery"
            trailing-icon="i-lucide-search"
            size="md"
            variant="outline"
            placeholder="Entrez le nom d'une station"
        />
        <div
            v-if="selectedStations.length > 0"
            class="max-h-44 overflow-y-auto shrink-0"
        >
            <ul>
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

        <USeparator v-if="selectedStations.length > 0" />

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
    </div>
</template>
