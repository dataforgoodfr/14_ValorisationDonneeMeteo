<script setup lang="ts">
import { formatDateForDisplay } from "~/utils/date";
import type { FilterOption } from "./filterBarTypes";

interface ActiveStringFilter {
    id: string;
    label: string;
    values: string[];
}

interface ActiveRangeFilter {
    id: string;
    label: string;
    type: string;
    range: { min: string; max: string };
}

const props = defineProps<{
    /** String filter groups that have at least one active value. */
    activeStringFilters: ActiveStringFilter[];
    /** Range filters that have an active min or max bound. */
    activeRangeFilters: ActiveRangeFilter[];
    /** Options map used to resolve a raw filter value (e.g. a station code)
     *  to its display label inside each chip. */
    filterOptions: Record<string, FilterOption[]>;
}>();

const emit = defineEmits<{
    toggleStringValue: [id: string, value: string];
    clear: [id: string];
}>();

function getValueLabel(fieldId: string, value: string): string {
    return (
        props.filterOptions[fieldId]?.find((v) => v.value === value)?.label ??
        value
    );
}

function getRangeDisplay(filter: ActiveRangeFilter): string {
    const { min, max } = filter.range;
    if (filter.type === "date-range") {
        const fMin = min ? formatDateForDisplay(min) : null;
        const fMax = max ? formatDateForDisplay(max) : null;
        if (fMin && fMax) return `${fMin} → ${fMax}`;
        if (fMin) return `≥ ${fMin}`;
        if (fMax) return `≤ ${fMax}`;
        return "";
    }
    const unit = filter.type === "number-range" ? "°C" : "";
    if (min && max) return `${min}${unit} → ${max}${unit}`;
    if (min) return `≥ ${min}${unit}`;
    if (max) return `≤ ${max}${unit}`;
    return "";
}
</script>

<template>
    <div class="flex flex-wrap items-center gap-x-4 gap-y-2">
        <!-- String filter groups -->
        <div
            v-for="filter in activeStringFilters"
            :key="filter.id"
            class="flex items-center gap-1.5"
        >
            <span class="text-xs font-semibold text-muted shrink-0">
                {{ filter.label }} ({{ filter.values.length }}) :
            </span>
            <div class="flex flex-wrap gap-1">
                <span
                    v-for="val in filter.values"
                    :key="val"
                    class="inline-flex items-center gap-1 pl-2 pr-1 py-0.5 rounded-full bg-primary/10 text-primary text-xs font-medium"
                >
                    {{ getValueLabel(filter.id, val) }}
                    <button
                        class="hover:bg-primary/20 rounded-full p-0.5 transition-colors"
                        @click="emit('toggleStringValue', filter.id, val)"
                    >
                        <UIcon name="i-lucide-x" class="size-2.5" />
                    </button>
                </span>
            </div>
            <button
                class="inline-flex items-center justify-center size-4 rounded-full bg-muted/20 hover:bg-error/20 hover:text-error transition-colors"
                title="Supprimer tous les filtres pour ce champ"
                @click="emit('clear', filter.id)"
            >
                <UIcon name="i-lucide-x" class="size-2.5" />
            </button>
        </div>

        <!-- Range filter chips -->
        <span
            v-for="filter in activeRangeFilters"
            :key="filter.id"
            class="inline-flex items-center gap-1.5 pl-2.5 pr-1 py-0.5 rounded-full bg-primary/10 text-primary text-xs font-medium"
        >
            <span>{{ filter.label }} : {{ getRangeDisplay(filter) }}</span>
            <button
                class="hover:bg-primary/20 rounded-full p-0.5 transition-colors"
                @click="emit('clear', filter.id)"
            >
                <UIcon name="i-lucide-x" class="size-2.5" />
            </button>
        </span>
    </div>
</template>
