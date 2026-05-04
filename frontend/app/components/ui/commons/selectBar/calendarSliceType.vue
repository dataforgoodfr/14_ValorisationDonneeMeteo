<script setup lang="ts">
import MonthOfYearPicker from "./monthOfYearPicker.vue";
import type { SelectBarAdapter } from "~/components/ui/commons/selectBar/types";

const adapter = inject<SelectBarAdapter>("selectBarAdapter")!;

const calendarSliceOptions = computed(() => {
    if (adapter.granularity.value === "year") {
        return [
            { label: "Tous les mois", value: "all" },
            { label: "Mois spécifique", value: "specific" },
        ];
    }
    return [
        { label: "Tous les jours", value: "all" },
        { label: "Jour spécifique", value: "specific" },
    ];
});

const pt = {
    root: { class: "relative w-36" },
    pcInputText: {
        root: {
            class: "w-full rounded-md ps-3 pe-9 py-1.5 text-sm text-highlighted bg-default ring ring-inset ring-accented focus-visible:ring-2 focus-visible:ring-primary focus:outline-none transition-colors",
        },
    },
    panel: {
        class: "relative w-64 bg-default rounded-lg shadow-lg ring ring-inset ring-accented p-3 mt-1 z-50",
    },
    header: { class: "hidden flex items-center justify-between mb-2" },
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
    selectMonth: {
        class: "hover:bg-elevated rounded px-1 py-0.5 cursor-pointer text-highlighted text-sm transition-colors",
    },
    selectYear: {
        class: "hover:bg-elevated rounded px-1 py-0.5 cursor-pointer text-highlighted text-sm transition-colors",
    },
    dayView: { class: "w-full border-collapse" },
    tableHeaderCell: { class: "hidden" },
    tableHeader: { class: "text-center pb-2" },
    weekDay: { class: "text-xs font-medium text-muted" },
    dayCell: { class: "text-center p-0" },
    day: ({
        context,
    }: {
        context: { selected: boolean; disabled: boolean };
    }) => ({
        class: [
            "mx-auto flex items-center justify-center rounded-full size-8 text-sm cursor-pointer transition-colors select-none focus:outline-none",
            context.selected
                ? "bg-primary text-inverted font-semibold"
                : "text-highlighted hover:bg-elevated",
            context.disabled
                ? "opacity-50 cursor-not-allowed pointer-events-none"
                : "",
        ],
    }),
};

const showDayPicker = computed(
    () =>
        adapter.granularity.value === "month" &&
        adapter.calendarSliceMode?.value === "specific",
);

const showMonthPicker = computed(
    () =>
        adapter.granularity.value === "year" &&
        adapter.calendarSliceMode?.value === "specific",
);
</script>

<template>
    <div class="flex gap-6">
        <div class="flex flex-col text-center gap-1">
            <p class="text-sm text-default">Période</p>
            <USelect
                v-model="adapter.calendarSliceMode!.value"
                :items="calendarSliceOptions"
                default-value="all"
            />
        </div>
        <div v-if="showDayPicker" class="flex flex-col text-center gap-1">
            <p class="text-sm text-default">Jour</p>
            <DatePicker
                v-model="adapter.calendarDatepickerDate!.value"
                date-format="dd"
                :pt="pt"
                unstyled
                append-to="self"
                show-icon
                icon-display="input"
                :show-other-months="false"
            />
        </div>
        <div v-if="showMonthPicker" class="flex flex-col text-center gap-1">
            <p class="text-sm text-default">Mois</p>
            <MonthOfYearPicker
                v-model="adapter.calendarDatepickerDate!.value"
            />
        </div>
    </div>
</template>
