<script setup lang="ts">
import { useIntersectionObserver } from "@vueuse/core";
import type { FilterField, FilterOption } from "./filterBarTypes";

const props = defineProps<{
    /** Field definition — used to tailor empty-state messaging and
     *  to decide whether typing should trigger an async search. */
    field: FilterField;
    /** Options to display in the list (pre-filtered by the parent for static
     *  fields, or the raw API results for async fields). */
    options: FilterOption[];
    /** Values of currently selected options (controlled). */
    selectedValues: string[];
    /** Current search input value (controlled). */
    searchQuery: string;
    /** When true, shows a loading spinner in the search input. */
    asyncPending?: boolean;
    /** When true, shows a sentinel at the bottom that triggers load-more on scroll. */
    hasMore?: boolean;
}>();

const emit = defineEmits<{
    "update:searchQuery": [query: string];
    search: [query: string];
    toggle: [value: string];
    clear: [];
    "load-more": [];
}>();

// Sentinel used to detect when the user scrolled to the bottom of the dropdown.
const sentinel = ref<HTMLElement | undefined>(undefined);
useIntersectionObserver(sentinel, ([entry]) => {
    if (entry?.isIntersecting) emit("load-more");
});

function getEmptyStateMessage(): string {
    return "Aucun résultat";
}

function onInput(query: string) {
    emit("update:searchQuery", query);
    if (props.field.type === "string-async") emit("search", query);
}
</script>

<template>
    <div class="p-2 border-b border-accented">
        <UInput
            :model-value="searchQuery"
            placeholder="Rechercher..."
            size="sm"
            icon="i-lucide-search"
            :loading="asyncPending"
            @update:model-value="onInput(String($event))"
        />
    </div>
    <div class="max-h-52 overflow-y-auto py-1">
        <label
            v-for="val in options"
            :key="val.value"
            class="flex items-center gap-2.5 px-3 py-2 text-sm cursor-pointer hover:bg-elevated transition-colors"
        >
            <input
                type="checkbox"
                class="accent-primary shrink-0"
                autocomplete="off"
                :checked="selectedValues.includes(val.value)"
                @change="emit('toggle', val.value)"
            />
            <span class="truncate">{{ val.label }}</span>
        </label>
        <p
            v-if="options.length === 0"
            class="px-3 py-2 text-sm text-muted italic"
        >
            {{ getEmptyStateMessage() }}
        </p>
        <div
            v-if="hasMore"
            ref="sentinel"
            class="px-3 py-2 text-center text-xs text-muted"
        >
            <span>Chargement...</span>
        </div>
    </div>
    <div
        v-if="selectedValues.length > 0"
        class="px-3 py-2 border-t border-accented flex items-center justify-between text-xs text-muted"
    >
        <span>{{ selectedValues.length }} sélectionné(s)</span>
        <button class="text-error hover:underline" @click="emit('clear')">
            Tout effacer
        </button>
    </div>
</template>
