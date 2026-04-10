<script setup lang="ts">
import { useRecordsChartStore } from "#imports";

const store = useRecordsChartStore();
const { territoriesFilter } = storeToRefs(store);
const { setTerritoryFilter } = store;

function onSelectTerritory(
    _event: PointerEvent,
    territory: { code: string; name: string },
) {
    setTerritoryFilter(territory);
}

const isTerritorySelected = computed(() => {
    return territoriesFilter.value.includes("FR");
});
</script>
<template>
    <div>
        <ul>
            <li
                v-if="!isTerritorySelected"
                :title="'France métropolitaine'"
                class="cursor-pointer pr-2 py-1 text-sm flex items-center justify-between"
                @click="
                    onSelectTerritory($event, {
                        code: 'FR',
                        name: 'France métropolitaine',
                    })
                "
            >
                <span class="truncate">France métropolitaine</span>
                <UIcon name="i-lucide-plus" class="shrink-0" />
            </li>
        </ul>
    </div>
</template>
