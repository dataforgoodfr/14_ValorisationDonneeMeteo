<script setup lang="ts">
import { onClickOutside } from "@vueuse/core";
import DayPicker from "./dayPicker.vue";
import { dateToStr, strToDate, formatDateForDisplay } from "~/utils/date";

export type FilterType = "string" | "date-range" | "number-range";

export interface FilterField {
    id: string;
    label: string;
    type: FilterType;
}

export interface FilterOption {
    value: string;
    label: string;
}

const props = defineProps<{
    fields: FilterField[];
    uniqueValues: Record<string, FilterOption[]>;
    stringFilters: Record<string, string[]>;
    rangeFilters: Record<string, { min: string; max: string }>;
}>();

const emit = defineEmits<{
    "update:stringFilter": [id: string, values: string[]];
    "update:rangeFilter": [id: string, min: string, max: string];
    clear: [id: string];
}>();

// Which dropdown is currently open
const openDropdown = ref<string | null>(null);

// Search query per string-filter dropdown
const searchInputs = reactive<Record<string, string>>({});

// Local state for number-range fields (strings)
const localRanges = reactive<Record<string, { min: string; max: string }>>({});

// Local state for date-range fields (Date objects for DayPicker)
const localDateRanges = reactive<Record<string, { start: Date; end: Date }>>(
    {},
);

// Close dropdowns when clicking outside the bar
const containerRef = ref<HTMLElement | null>(null);
onClickOutside(containerRef, () => {
    openDropdown.value = null;
});

function getFilterCount(id: string): number {
    if (props.stringFilters[id]?.length) return props.stringFilters[id].length;
    if (props.rangeFilters[id]?.min || props.rangeFilters[id]?.max) return 1;
    return 0;
}

function toggleDropdown(id: string) {
    if (openDropdown.value === id) {
        openDropdown.value = null;
        return;
    }
    const field = props.fields.find((f) => f.id === id);
    if (field?.type === "date-range") {
        const stored = props.rangeFilters[id];
        localDateRanges[id] = {
            start: stored?.min ? strToDate(stored.min) : new Date(),
            end: stored?.max ? strToDate(stored.max) : new Date(),
        };
    } else {
        localRanges[id] = {
            min: props.rangeFilters[id]?.min ?? "",
            max: props.rangeFilters[id]?.max ?? "",
        };
    }
    openDropdown.value = id;
}

function toggleStringValue(id: string, value: string) {
    const current = props.stringFilters[id] ?? [];
    const isSelected = current.includes(value);
    emit(
        "update:stringFilter",
        id,
        isSelected ? current.filter((v) => v !== value) : [...current, value],
    );
}

function isStringValueSelected(id: string, value: string): boolean {
    return (props.stringFilters[id] ?? []).includes(value);
}

function getFilteredUniqueValues(id: string): FilterOption[] {
    const allValues = props.uniqueValues[id] ?? [];
    const search = (searchInputs[id] ?? "").toLowerCase();
    if (!search) return allValues;
    return allValues.filter((v) => v.label.toLowerCase().includes(search));
}

function getValueLabel(fieldId: string, value: string): string {
    return (
        props.uniqueValues[fieldId]?.find((v) => v.value === value)?.label ??
        value
    );
}

function updateRange(id: string, key: "min" | "max", value: string) {
    const localRange = localRanges[id];
    if (!localRange) {
        console.error(
            `The local range for '${id}' must have been initialized before in toggleDropdown`,
        );
        return;
    }
    localRange[key] = value;
    emit("update:rangeFilter", id, localRange.min, localRange.max);
}

function updateDateRange(id: string, key: "start" | "end", date: Date) {
    const localDateRange = localDateRanges[id];
    if (!localDateRange) {
        console.error(
            `The local date range for '${id}' must have been initialized before in toggleDropdown`,
        );
        return;
    }
    localDateRange[key] = date;
    emit(
        "update:rangeFilter",
        id,
        dateToStr(localDateRange.start),
        dateToStr(localDateRange.end),
    );
}

// Active filters derived from props
const activeStringFilters = computed(() =>
    Object.entries(props.stringFilters)
        .filter(([, values]) => values.length > 0)
        .map(([id, values]) => ({
            id,
            label: props.fields.find((f) => f.id === id)?.label ?? id,
            values,
        })),
);

const activeRangeFilters = computed(() =>
    Object.entries(props.rangeFilters)
        .filter(([, range]) => range.min || range.max)
        .map(([id, range]) => {
            const field = props.fields.find((f) => f.id === id);
            return {
                id,
                label: field?.label ?? id,
                type: field?.type ?? "number-range",
                range,
            };
        }),
);

const hasAnyFilter = computed(
    () =>
        activeStringFilters.value.length > 0 ||
        activeRangeFilters.value.length > 0,
);

function clearFilter(id: string) {
    emit("clear", id);
}

function getRangeDisplay(filter: {
    range: { min: string; max: string };
    type: string;
}): string {
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
    <div
        ref="containerRef"
        class="flex flex-col gap-3 px-4 py-3.5 border-b border-accented"
    >
        <div class="flex items-start gap-4">
            <!-- Filter buttons + chips -->
            <div class="flex flex-col gap-3 flex-1 min-w-0">
                <!-- Filter buttons row -->
                <div class="flex items-center gap-2 flex-wrap">
                    <!-- One button per filter field -->
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
                            @click="toggleDropdown(field.id)"
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
                                    openDropdown === field.id
                                        ? 'i-lucide-chevron-up'
                                        : 'i-lucide-chevron-down'
                                "
                                class="size-3 opacity-50"
                            />
                        </button>

                        <!-- Dropdown panel -->
                        <div
                            v-if="openDropdown === field.id"
                            class="absolute top-full left-0 z-50 mt-1 rounded-lg border border-accented bg-default shadow-xl"
                            :class="
                                field.type === 'date-range' ? 'w-auto' : 'w-64'
                            "
                        >
                            <!-- String filter: search + checkboxes -->
                            <template v-if="field.type === 'string'">
                                <div class="p-2 border-b border-accented">
                                    <UInput
                                        v-model="searchInputs[field.id]"
                                        placeholder="Rechercher..."
                                        size="sm"
                                        icon="i-lucide-search"
                                    />
                                </div>
                                <div class="max-h-52 overflow-y-auto py-1">
                                    <label
                                        v-for="val in getFilteredUniqueValues(
                                            field.id,
                                        )"
                                        :key="val.value"
                                        class="flex items-center gap-2.5 px-3 py-2 text-sm cursor-pointer hover:bg-elevated transition-colors"
                                    >
                                        <input
                                            type="checkbox"
                                            class="accent-primary shrink-0"
                                            autocomplete="off"
                                            :checked="
                                                isStringValueSelected(
                                                    field.id,
                                                    val.value,
                                                )
                                            "
                                            @change="
                                                toggleStringValue(
                                                    field.id,
                                                    val.value,
                                                )
                                            "
                                        />
                                        <span class="truncate">{{
                                            val.label
                                        }}</span>
                                    </label>
                                    <p
                                        v-if="
                                            getFilteredUniqueValues(field.id)
                                                .length === 0
                                        "
                                        class="px-3 py-2 text-sm text-muted italic"
                                    >
                                        Aucun résultat
                                    </p>
                                </div>
                                <!-- Selection count -->
                                <div
                                    v-if="
                                        (stringFilters[field.id] ?? []).length >
                                        0
                                    "
                                    class="px-3 py-2 border-t border-accented flex items-center justify-between text-xs text-muted"
                                >
                                    <span>
                                        {{
                                            (stringFilters[field.id] ?? [])
                                                .length
                                        }}
                                        sélectionné(s)
                                    </span>
                                    <button
                                        class="text-error hover:underline"
                                        @click="clearFilter(field.id)"
                                    >
                                        Tout effacer
                                    </button>
                                </div>
                            </template>

                            <!-- Number range filter: min / max inputs -->
                            <template v-else-if="field.type === 'number-range'">
                                <div class="p-3 flex flex-col gap-3">
                                    <div class="flex flex-col gap-1">
                                        <label
                                            class="text-xs font-medium text-muted"
                                            >Minimum</label
                                        >
                                        <UInput
                                            type="number"
                                            :model-value="
                                                localRanges[field.id]?.min ?? ''
                                            "
                                            size="sm"
                                            placeholder="Min"
                                            @update:model-value="
                                                (v) =>
                                                    updateRange(
                                                        field.id,
                                                        'min',
                                                        String(v),
                                                    )
                                            "
                                        />
                                    </div>
                                    <div class="flex flex-col gap-1">
                                        <label
                                            class="text-xs font-medium text-muted"
                                            >Maximum</label
                                        >
                                        <UInput
                                            type="number"
                                            :model-value="
                                                localRanges[field.id]?.max ?? ''
                                            "
                                            size="sm"
                                            placeholder="Max"
                                            @update:model-value="
                                                (v) =>
                                                    updateRange(
                                                        field.id,
                                                        'max',
                                                        String(v),
                                                    )
                                            "
                                        />
                                    </div>
                                    <button
                                        v-if="
                                            rangeFilters[field.id]?.min ||
                                            rangeFilters[field.id]?.max
                                        "
                                        class="text-xs text-error hover:underline text-left"
                                        @click="clearFilter(field.id)"
                                    >
                                        Effacer
                                    </button>
                                </div>
                            </template>

                            <!-- Date range filter: DayPicker -->
                            <template v-else>
                                <div class="p-3 flex flex-col gap-3">
                                    <DayPicker
                                        :start-date="
                                            localDateRanges[field.id]!.start
                                        "
                                        :end-date="
                                            localDateRanges[field.id]!.end
                                        "
                                        @update:start-date="
                                            (d) =>
                                                updateDateRange(
                                                    field.id,
                                                    'start',
                                                    d,
                                                )
                                        "
                                        @update:end-date="
                                            (d) =>
                                                updateDateRange(
                                                    field.id,
                                                    'end',
                                                    d,
                                                )
                                        "
                                    />
                                    <button
                                        v-if="
                                            rangeFilters[field.id]?.min ||
                                            rangeFilters[field.id]?.max
                                        "
                                        class="text-xs text-error hover:underline text-left"
                                        @click="clearFilter(field.id)"
                                    >
                                        Effacer
                                    </button>
                                </div>
                            </template>
                        </div>
                    </div>
                </div>

                <!-- Active filter chips -->
                <div
                    v-if="hasAnyFilter"
                    class="flex flex-wrap items-center gap-x-4 gap-y-2"
                >
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
                                    @click="toggleStringValue(filter.id, val)"
                                >
                                    <UIcon name="i-lucide-x" class="size-2.5" />
                                </button>
                            </span>
                        </div>
                        <!-- Clear all for this field -->
                        <button
                            class="inline-flex items-center justify-center size-4 rounded-full bg-muted/20 hover:bg-error/20 hover:text-error transition-colors"
                            title="Supprimer tous les filtres pour ce champ"
                            @click="clearFilter(filter.id)"
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
                        <span
                            >{{ filter.label }} :
                            {{ getRangeDisplay(filter) }}</span
                        >
                        <button
                            class="hover:bg-primary/20 rounded-full p-0.5 transition-colors"
                            @click="clearFilter(filter.id)"
                        >
                            <UIcon name="i-lucide-x" class="size-2.5" />
                        </button>
                    </span>
                </div>
            </div>
            <!-- end left column -->

            <!-- Right-side actions slot (e.g. record type toggle) -->
            <slot name="actions" />
        </div>
        <!-- end outer row -->
    </div>
</template>
