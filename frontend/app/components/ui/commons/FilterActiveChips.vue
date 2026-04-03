<script setup lang="ts">
import { formatDateForDisplay } from "~/utils/date";
import type {
    FilterField,
    FilterOption,
    FilterValue,
    StringFilterValue,
    RangeFilterValue,
    DateFilterValue,
} from "./filterBarTypes";

interface StringChip {
    kind: "string";
    id: string;
    label: string;
    values: { value: string; label: string }[];
}

interface RangeChip {
    kind: "range";
    id: string;
    label: string;
    display: string;
}

type ActiveChip = StringChip | RangeChip;

const props = defineProps<{
    /** Field definitions — used to resolve display labels. */
    fields: FilterField[];
    /** Currently active filters, keyed by field id. */
    filters: Record<string, FilterValue>;
    /** Options map used to resolve a raw filter value (e.g. a station code)
     *  to its display label inside each chip. */
    filterOptions: Record<string, FilterOption[]>;
}>();

const emit = defineEmits<{
    toggleStringValue: [id: string, value: string];
    clear: [id: string];
}>();

const labelFor = (id: string) =>
    props.fields.find((f) => f.id === id)?.label ?? id;

function toStringChip(id: string, f: StringFilterValue): StringChip | null {
    if (f.values.length === 0) return null;
    return {
        kind: "string",
        id,
        label: labelFor(id),
        values: f.values.map((v) => ({
            value: v,
            label:
                props.filterOptions[id]?.find((o) => o.value === v)?.label ?? v,
        })),
    };
}

function toRangeChip(
    id: string,
    f: RangeFilterValue | DateFilterValue,
): RangeChip | null {
    let min: string | undefined;
    let max: string | undefined;
    let unit: string;
    let display: string;

    if (f.type === "number-range") {
        min = f.min;
        max = f.max;
        unit = "°C";
    } else {
        min = f.min ? formatDateForDisplay(f.min) : undefined;
        max = f.max ? formatDateForDisplay(f.max) : undefined;
        unit = "";
    }

    if (!min && !max) {
        return null;
    }

    if (min && max) {
        display = `${min}${unit} → ${max}${unit}`;
    } else if (min) {
        display = `≥ ${min}${unit}`;
    } else {
        display = `≤ ${max}${unit}`;
    }

    return { kind: "range", id, label: labelFor(id), display };
}

// There are only two types of chips, so we must convert the input filters into one of these two types.
const activeChips = computed<ActiveChip[]>(() =>
    // Use flatMap to automatically discard filters that couldn't be converted into chips.
    Object.entries(props.filters).flatMap(([id, f]) => {
        let chip: ActiveChip | null;
        if (f.type === "string") {
            chip = toStringChip(id, f);
        } else {
            chip = toRangeChip(id, f);
        }
        return chip ? [chip] : [];
    }),
);
</script>

<template>
    <div class="flex flex-wrap items-center gap-x-4 gap-y-2">
        <template v-for="chip in activeChips" :key="chip.id">
            <!-- String filter group -->
            <div
                v-if="chip.kind === 'string'"
                class="flex items-center gap-1.5"
            >
                <span class="text-xs font-semibold text-muted shrink-0">
                    {{ chip.label }} ({{ chip.values.length }}) :
                </span>
                <div class="flex flex-wrap gap-1">
                    <span
                        v-for="val in chip.values"
                        :key="val.value"
                        class="inline-flex items-center gap-1 pl-2 pr-1 py-0.5 rounded-full bg-primary/10 text-primary text-xs font-medium"
                    >
                        {{ val.label }}
                        <button
                            class="hover:bg-primary/20 rounded-full p-0.5 transition-colors"
                            @click="
                                emit('toggleStringValue', chip.id, val.value)
                            "
                        >
                            <UIcon name="i-lucide-x" class="size-2.5" />
                        </button>
                    </span>
                </div>
                <button
                    class="inline-flex items-center justify-center size-4 rounded-full bg-muted/20 hover:bg-error/20 hover:text-error transition-colors"
                    title="Supprimer tous les filtres pour ce champ"
                    @click="emit('clear', chip.id)"
                >
                    <UIcon name="i-lucide-x" class="size-2.5" />
                </button>
            </div>

            <!-- Range/date chip -->
            <span
                v-else
                class="inline-flex items-center gap-1.5 pl-2.5 pr-1 py-0.5 rounded-full bg-primary/10 text-primary text-xs font-medium"
            >
                <span>{{ chip.label }} : {{ chip.display }}</span>
                <button
                    class="hover:bg-primary/20 rounded-full p-0.5 transition-colors"
                    @click="emit('clear', chip.id)"
                >
                    <UIcon name="i-lucide-x" class="size-2.5" />
                </button>
            </span>
        </template>
    </div>
</template>
