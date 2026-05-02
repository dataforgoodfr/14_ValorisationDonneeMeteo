<template>
    <div class="flex items-center">
        <ul class="grid grid-cols-1 md:grid-cols-3">
            <li
                v-for="station in sortedStations"
                :key="station.code"
                class="flex flex-col justify-center gap-0.5 px-3 py-2 rounded transition-colors cursor-default select-none"
                @mouseenter="emit('update:hoveredCode', station.code)"
                @mouseleave="emit('update:hoveredCode', null)"
            >
                <div class="flex items-center gap-3">
                    <span
                        class="text-base truncate transition-colors"
                        :class="
                            station.code === hoveredCode ? 'text-primary' : ''
                        "
                        >{{ station.nom }}</span
                    >
                </div>
                <div class="flex items-center gap-3 pl-1 text-xs text-muted">
                    <UTooltip :text="`Altitude : ${station.alt} m`">
                        <span class="flex items-center gap-1">
                            <UIcon
                                name="i-lucide-mountain"
                                class="size-4 shrink-0 opacity-40"
                            />
                            {{ station.alt }} m
                        </span>
                    </UTooltip>
                    <UTooltip
                        v-if="station.classe !== null"
                        :text="`Classe de la station : ${station.classe}`"
                    >
                        <span class="flex items-center gap-1">
                            <UIcon
                                :name="classeIcon(station.classe)"
                                class="size-4 shrink-0 opacity-40"
                            />
                            Cl. {{ station.classe }}
                        </span>
                    </UTooltip>
                    <UTooltip
                        :text="`Année de création : ${station.annee_creation}`"
                    >
                        <span class="flex items-center gap-1">
                            <UIcon
                                name="i-lucide-calendar-days"
                                class="size-4 shrink-0 opacity-40"
                            />
                            {{ station.annee_creation }}
                        </span>
                    </UTooltip>
                </div>
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

function classeIcon(classe: number): string {
    if (classe <= 1) return "i-lucide-wifi";
    if (classe === 2) return "i-lucide-wifi-high";
    if (classe === 3) return "i-lucide-wifi-low";
    return "i-lucide-wifi-low";
}
</script>
