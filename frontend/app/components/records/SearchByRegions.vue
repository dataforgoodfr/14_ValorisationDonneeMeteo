<script setup lang="ts">
import { regions } from "~/data/records/regions";
import { normalizeString } from "~/utils/string";
import { useRecordsChartStore } from "#imports";

const props = defineProps({
    searchQuery: {
        type: String,
        default: "",
    },
});

const searchQueryRef = toRef(props, "searchQuery");

const store = useRecordsChartStore();
const { regionsFilter } = storeToRefs(store);
const { setRegionFilter } = store;

function onSelectRegion(
    _event: PointerEvent,
    region: { code: string; name: string },
) {
    setRegionFilter(region);
}

const unselectedFilteredRegions = computed(() => {
    const regionCodesFilter = regionsFilter.value;

    return regions.filter((region) => {
        if (!searchQueryRef.value || searchQueryRef.value.trim() === "") {
            return !regionCodesFilter.includes(region.code);
        }

        const normalizedRegion = normalizeString(region.name);
        const searchQueryLower = normalizeString(
            searchQueryRef.value,
        ).toLowerCase();
        const regionNameLower = normalizedRegion.toLowerCase();

        return regionNameLower.includes(searchQueryLower);
    });
});
</script>
<template>
    <div class="overflow-y-auto">
        <ul>
            <li
                v-for="region in unselectedFilteredRegions"
                :key="`filtered-${region.code}`"
                :title="`${region.name} (${region.code})`"
                class="cursor-pointer pr-2 py-1 text-sm flex items-center justify-between"
                @click="onSelectRegion($event, region)"
            >
                <span class="truncate">{{ region.name }}</span>
                <UIcon name="i-lucide-plus" class="shrink-0" />
            </li>
        </ul>
    </div>
</template>
