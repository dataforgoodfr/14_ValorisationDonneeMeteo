<template>
    <div class="flex items-center">
        <ul class="list-grid">
            <li
                v-for="station in sortedStations"
                :key="station.code"
                class="flex justify-start items-center gap-3 px-3 py-1.5 h-12 rounded transition-colors cursor-default select-none"
                @mouseenter="emit('update:hoveredCode', station.code)"
                @mouseleave="emit('update:hoveredCode', null)"
            >
                <UBadge
                    :label="`P${station.classe}`"
                    variant="soft"
                    size="xl"
                    class="shrink-0"
                />
                <span
                    class="text-base truncate transition-colors"
                    :class="station.code === hoveredCode ? 'text-primary' : ''"
                    >{{ station.nom }}</span
                >
            </li>
        </ul>
    </div>
</template>

<script setup lang="ts">
import type { ItnStation } from "~/types/api";

const props = defineProps<{
    stations: ItnStation[];
    hoveredCode: string | null;
}>();

const emit = defineEmits<{
    "update:hoveredCode": [code: string | null];
}>();

const sortedStations = computed(() =>
    [...props.stations].sort((a, b) => a.nom.localeCompare(b.nom, "fr")),
);
</script>

<style>
.list-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
}
</style>
