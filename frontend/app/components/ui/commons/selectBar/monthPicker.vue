<script setup lang="ts">
import DatePicker from "primevue/datepicker";
import { useCustomDate } from "#imports";
import type { SelectBarAdapter } from "~/components/ui/commons/selectBar/types";

const localStartDate = defineModel<Date | undefined>("startDate");
const localEndDate = defineModel<Date | undefined>("endDate");

const adapter = inject<SelectBarAdapter>("selectBarAdapter")!;
const dates = useCustomDate();

const minStartDate = computed(() => {
    if (!localEndDate.value) return dates.absoluteMinDataDate.value;
    const d = new Date(localEndDate.value);
    d.setFullYear(d.getFullYear() - 50);
    return d;
});

const maxEndDate = computed(() => {
    if (!localStartDate.value) return dates.today.value;
    const d = new Date(localStartDate.value);
    d.setFullYear(d.getFullYear() + 50);
    const max = adapter.maxDate?.value ?? dates.today.value;
    return d < max ? d : max;
});

const pt = {
    root: { class: "relative w-36" },
    pcInputText: {
        root: {
            class: "w-full rounded-md ps-3 pe-9 py-1.5 text-sm text-highlighted bg-default ring ring-inset ring-accented focus-visible:ring-2 focus-visible:ring-primary focus:outline-none transition-colors",
        },
    },
    panel: {
        class: "relative w-48 bg-default rounded-lg shadow-lg ring ring-inset ring-accented p-3 mt-1 z-50",
    },
    header: { class: "flex items-center justify-between mb-2" },
    pcPrevButton: {
        root: {
            class: "rounded-md p-1 hover:bg-elevated text-muted hover:text-highlighted transition-colors",
        },
    },
    pcNextButton: {
        root: {
            class: "rounded-md p-1 hover:bg-elevated text-muted hover:text-highlighted transition-colors",
        },
    },
    inputIconContainer: {
        class: "absolute inset-y-0 end-0 flex items-center pe-3 pointer-events-none",
    },
    inputIcon: { class: "shrink-0 text-dimmed size-4" },
    title: { class: "flex gap-1 text-sm font-medium text-highlighted" },
    selectYear: {
        class: "hover:bg-elevated rounded px-1 py-0.5 cursor-pointer text-highlighted text-sm transition-colors",
    },
    monthView: { class: "grid grid-cols-3 gap-1 mt-1" },
    yearView: { class: "grid grid-cols-3 gap-1 mt-1" },
    month: ({
        context,
    }: {
        context: { selected: boolean; disabled: boolean };
    }) => ({
        class: [
            "rounded-md text-center text-sm px-2 py-1.5 cursor-pointer transition-colors select-none",
            context.selected
                ? "bg-primary text-inverted font-semibold"
                : "text-highlighted hover:bg-elevated",
            context.disabled
                ? "opacity-50 cursor-not-allowed pointer-events-none"
                : "",
        ],
    }),
    year: ({
        context,
    }: {
        context: { selected: boolean; disabled: boolean };
    }) => ({
        class: [
            "rounded-md text-center text-sm px-2 py-1.5 cursor-pointer transition-colors select-none",
            context.selected
                ? "bg-primary text-inverted font-semibold"
                : "text-highlighted hover:bg-elevated",
            context.disabled
                ? "opacity-50 cursor-not-allowed pointer-events-none"
                : "",
        ],
    }),
};
</script>

<template>
    <div id="container-monthly-picker" class="flex gap-2">
        <div class="flex flex-col text-center gap-1">
            <p class="text-sm text-default">Mois de début</p>
            <DatePicker
                v-model="localStartDate"
                :min-date="minStartDate"
                :max-date="localEndDate"
                view="month"
                date-format="mm/yy"
                :pt="pt"
                unstyled
                append-to="self"
                show-icon
                icon-display="input"
            />
        </div>
        <div class="pt-7 self-center">
            <UIcon name="i-lucide-arrow-right" />
        </div>
        <div class="flex flex-col text-center gap-1">
            <p class="text-sm text-default">Mois de fin</p>
            <DatePicker
                v-model="localEndDate"
                :min-date="localStartDate"
                :max-date="maxEndDate"
                view="month"
                date-format="mm/yy"
                :pt="pt"
                unstyled
                append-to="self"
                show-icon
                icon-display="input"
            />
        </div>
    </div>
</template>
