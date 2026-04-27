<template>
    <div class="flex flex-col min-w-0 flex-1">
        <ul class="overflow-y-auto flex flex-wrap">
            <li
                v-for="station in sortedStations"
                :key="station.code"
                class="flex items-center gap-3 px-3 py-1.5 h-16 rounded transition-colors cursor-default select-none w-1/3"
                @mouseenter="emit('update:hoveredCode', station.code)"
                @mouseleave="emit('update:hoveredCode', null)"
            >
                <UBadge
                    :label="ITN_STATION_WEIGHT"
                    variant="soft"
                    size="xl"
                    class="shrink-0"
                />
                <span
                    class="text-sm truncate transition-colors"
                    :class="station.code === hoveredCode ? 'text-primary' : ''"
                >{{ station.nom }}</span>
            </li>
        </ul>
    </div>
</template>

<script setup lang="ts">
import type { ItnMappableStation } from "~/types/api";
import { ITN_STATION_WEIGHT } from "~/constants/itn";

const props = defineProps<{
    stations: ItnMappableStation[];
    hoveredCode: string | null;
}>();

const emit = defineEmits<{
    "update:hoveredCode": [code: string | null];
}>();

const sortedStations = computed(() =>
    [...props.stations].sort((a, b) => a.nom.localeCompare(b.nom, "fr")),
);
</script>
