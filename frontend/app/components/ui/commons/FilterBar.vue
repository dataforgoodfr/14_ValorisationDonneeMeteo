<script setup lang="ts">
import { onClickOutside } from "@vueuse/core";
import type { FilterField, FilterOption, FilterValue } from "./filterBarTypes";
import FilterDropdownString from "./FilterDropdownString.vue";
import FilterDropdownRange from "./FilterDropdownRange.vue";
import FilterDropdownDateRange from "./FilterDropdownDateRange.vue";
import FilterActiveChips from "./FilterActiveChips.vue";
export type {
    FilterType,
    FilterField,
    FilterOption,
    FilterValue,
} from "./filterBarTypes";

const props = defineProps<{
    /** Field definitions that determine which filters are shown and their type. */
    fields: FilterField[];
    /** Available options for each field, keyed by field id. For async fields,
     *  this should include both live search results and options for already-selected
     *  values so that active chips can always resolve labels. */
    filterOptions: Record<string, FilterOption[]>;
    /** Currently active filters, keyed by field id. */
    filters: Record<string, FilterValue>;
    /** Loading state per field id, shown as a spinner in the search input. */
    asyncPending?: Record<string, boolean>;
    /** Whether more pages are available per field id, used to show infinite scroll sentinel. */
    asyncHasMore?: Record<string, boolean>;
}>();

const emit = defineEmits<{
    "update:filter": [id: string, value: FilterValue];
    clear: [id: string];
    search: [id: string, query: string];
    "load-more": [id: string];
}>();

// Only one dropdown can be open at a time — single refs suffice for all local state.
const openField = ref<FilterField | null>(null);
const searchQuery = ref("");
const localRange = ref<{ min: string; max: string }>({ min: "", max: "" });
const localDateRange = ref<{ start: Date | undefined; end: Date | undefined }>({
    start: undefined,
    end: undefined,
});

// Prop access helpers — consolidate ?? in one place, not scattered across the template.
const stringValuesFor = (id: string): string[] => {
    const f = props.filters[id];
    return f?.type === "string" ? f.values : [];
};
const filterOptionsFor = (id: string): FilterOption[] =>
    props.filterOptions[id] ?? [];

const containerRef = ref<HTMLElement | null>(null);
onClickOutside(containerRef, () => {
    openField.value = null;
});

function getFilterCount(id: string): number {
    const f = props.filters[id];
    if (!f) {
        return 0;
    }
    if (f.type === "string") {
        return f.values.length;
    }
    return f.min || f.max ? 1 : 0;
}

function toggleDropdown(field: FilterField) {
    if (openField.value?.id === field.id) {
        openField.value = null;
        return;
    }
    const f = props.filters[field.id];
    if (field.type === "date-range") {
        const stored = f?.type === "date-range" ? f : undefined;
        localDateRange.value = {
            start: stored?.min,
            end: stored?.max,
        };
    } else {
        const stored = f?.type === "number-range" ? f : undefined;
        localRange.value = { min: stored?.min ?? "", max: stored?.max ?? "" };
    }
    searchQuery.value = "";
    openField.value = field;
    if (field.type === "string-async") {
        emit("search", field.id, "");
    }
}

function getDisplayedOptions(field: FilterField): FilterOption[] {
    if (field.type === "string-async") {
        return filterOptionsFor(field.id);
    }
    const allValues = filterOptionsFor(field.id);
    const search = searchQuery.value.toLowerCase();
    if (!search) {
        return allValues;
    }
    return allValues.filter((v) => v.label.toLowerCase().includes(search));
}

function toggleStringValue(id: string, value: string) {
    const current = stringValuesFor(id);
    const next = current.includes(value)
        ? current.filter((v) => v !== value)
        : [...current, value];
    emit("update:filter", id, { type: "string", values: next });
}

function onUpdateRange(key: "min" | "max", value: string) {
    localRange.value[key] = value;
    const { id } = openField.value!;
    emit("update:filter", id, { type: "number-range", ...localRange.value });
}

function onUpdateDateRange(key: "start" | "end", date: Date | undefined) {
    localDateRange.value[key] = date;
    const { id } = openField.value!;
    emit("update:filter", id, {
        type: "date-range",
        min: localDateRange.value.start,
        max: localDateRange.value.end,
    });
}

function onClear(id: string) {
    if (openField.value?.id === id) {
        localRange.value = { min: "", max: "" };
        localDateRange.value = { start: undefined, end: undefined };
    }
    emit("clear", id);
}

const hasAnyFilter = computed(() => Object.keys(props.filters).length > 0);
</script>

<template>
    <div
        ref="containerRef"
        class="flex flex-col gap-3 px-4 py-3.5 border-b border-accented"
    >
        <div class="flex items-start gap-4">
            <div class="flex flex-col gap-3 flex-1 min-w-0">
                <!-- Filter buttons row -->
                <div class="flex items-center gap-2 flex-wrap">
                    <div
                        v-for="field in fields"
                        :key="field.id"
                        class="relative"
                    >
                        <button
                            class="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-md border transition-colors cursor-pointer"
                            :class="
                                getFilterCount(field.id) > 0
                                    ? 'bg-primary/10 border-primary/40 text-primary'
                                    : 'border-accented hover:bg-elevated'
                            "
                            @click="toggleDropdown(field)"
                        >
                            <UIcon
                                name="i-lucide-filter"
                                class="size-3.5 opacity-60"
                            />
                            <span>{{ field.label }}</span>
                            <span
                                v-if="getFilterCount(field.id) > 0"
                                class="inline-flex items-center justify-center min-w-[1.1rem] h-[1.1rem] px-1 text-[10px] font-bold rounded-full bg-primary text-white"
                            >
                                {{ getFilterCount(field.id) }}
                            </span>
                            <UIcon
                                :name="
                                    openField?.id === field.id
                                        ? 'i-lucide-chevron-up'
                                        : 'i-lucide-chevron-down'
                                "
                                class="size-3 opacity-50"
                            />
                        </button>

                        <!-- Dropdown panel -->
                        <div
                            v-if="openField?.id === field.id"
                            class="absolute top-full left-0 z-50 mt-1 rounded-lg border border-accented bg-default shadow-xl"
                            :class="
                                field.type === 'date-range' ? 'w-auto' : 'w-64'
                            "
                        >
                            <FilterDropdownString
                                v-if="
                                    field.type === 'string' ||
                                    field.type === 'string-async'
                                "
                                :field="field"
                                :options="getDisplayedOptions(field)"
                                :selected-values="stringValuesFor(field.id)"
                                :search-query="searchQuery"
                                :async-pending="asyncPending?.[field.id]"
                                :has-more="asyncHasMore?.[field.id]"
                                @update:search-query="searchQuery = $event"
                                @search="emit('search', field.id, $event)"
                                @toggle="toggleStringValue(field.id, $event)"
                                @clear="onClear(field.id)"
                                @load-more="emit('load-more', field.id)"
                            />
                            <FilterDropdownRange
                                v-else-if="field.type === 'number-range'"
                                :min="localRange.min"
                                :max="localRange.max"
                                :has-filter="getFilterCount(field.id) > 0"
                                @update:min="onUpdateRange('min', $event)"
                                @update:max="onUpdateRange('max', $event)"
                                @clear="onClear(field.id)"
                            />
                            <FilterDropdownDateRange
                                v-else
                                :start-date="localDateRange.start"
                                :end-date="localDateRange.end"
                                :has-filter="getFilterCount(field.id) > 0"
                                @update:start-date="
                                    onUpdateDateRange('start', $event)
                                "
                                @update:end-date="
                                    onUpdateDateRange('end', $event)
                                "
                                @clear="onClear(field.id)"
                            />
                        </div>
                    </div>
                </div>

                <!-- Active filter chips -->
                <FilterActiveChips
                    v-if="hasAnyFilter"
                    :fields="fields"
                    :filters="filters"
                    :filter-options="filterOptions"
                    @toggle-string-value="toggleStringValue"
                    @clear="onClear($event)"
                />
            </div>

            <!-- Right-side actions slot -->
            <slot name="actions" />
        </div>
    </div>
</template>
