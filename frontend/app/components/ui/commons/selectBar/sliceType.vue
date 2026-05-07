<script setup lang="ts">
import MonthOfYearPicker from "./monthOfYearPicker.vue";
import type {
    SliceType,
    SelectBarAdapter,
} from "~/components/ui/commons/selectBar/types";

const adapter = inject<SelectBarAdapter>("selectBarAdapter")!;

function isSliceType(val: unknown): val is SliceType {
    return val === "full" || val === "month_of_year" || val === "day_of_month";
}

const isCalendarMode = computed(
    () =>
        adapter.calendarSliceMode !== undefined &&
        adapter.chartType?.value === "calendar",
);

// Calendar mode options
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

// Standard mode options — depends on granularity
const averagingOptions = computed(() => {
    if (adapter.granularity.value === "year") {
        return [
            { label: "Année", value: "full" },
            { label: "Mois", value: "month_of_year" },
            { label: "Jour", value: "day_of_month" },
        ];
    }
    if (adapter.granularity.value === "month") {
        return [
            { label: "Mois", value: "full" },
            { label: "Jour", value: "day_of_month" },
        ];
    }
    return [{ label: "Jour", value: "day_of_month" }];
});

// Disabled only when granularity = day (except calendar mode, always enabled)
const isAveragingDisabled = computed(() => {
    if (isCalendarMode.value) return false;
    return adapter.granularity.value === "day";
});

// Informational value shown when disabled (granularity = day)
const lockedAveragingValue = computed<SliceType>(() => "day_of_month");

// Date picker styling
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
    yearView: { class: "grid grid-cols-3 gap-1 mt-1" },
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
const ptDayMonthOfYear = {
    ...pt,
    selectYear: { class: "hidden" },
    header: { class: "flex items-center justify-between mb-2" },
    tableHeaderCell: {},
};

// Standard mode pickers
const showDayOfMonthPicker = computed(
    () =>
        !isCalendarMode.value &&
        adapter.granularity.value === "month" &&
        adapter.sliceType?.value === "day_of_month",
);

const showMonthOfYearPicker = computed(
    () =>
        !isCalendarMode.value &&
        adapter.granularity.value === "year" &&
        adapter.sliceType?.value === "month_of_year",
);

const showDayMonthOfYearPicker = computed(
    () =>
        !isCalendarMode.value &&
        adapter.granularity.value === "year" &&
        adapter.sliceType?.value === "day_of_month",
);

// Calendar mode pickers
const showCalendarDayPicker = computed(
    () =>
        isCalendarMode.value &&
        adapter.granularity.value === "month" &&
        adapter.calendarSliceMode?.value === "specific",
);

const showCalendarMonthPicker = computed(
    () =>
        isCalendarMode.value &&
        adapter.granularity.value === "year" &&
        adapter.calendarSliceMode?.value === "specific",
);
</script>

<template>
    <div class="flex gap-6">
        <div class="flex flex-col text-center gap-1">
            <p class="text-sm text-default">
                {{ isCalendarMode ? "Période" : "Moyenner par" }}
            </p>
            <USelect
                v-if="isCalendarMode"
                v-model="adapter.calendarSliceMode!.value"
                :items="calendarSliceOptions"
                default-value="all"
            />
            <USelect
                v-else
                :model-value="
                    isAveragingDisabled
                        ? lockedAveragingValue
                        : (adapter.sliceType?.value ?? 'full')
                "
                :disabled="isAveragingDisabled"
                :items="averagingOptions"
                @update:model-value="
                    (val) => {
                        if (adapter.sliceType && isSliceType(val))
                            adapter.sliceType.value = val;
                    }
                "
            />
        </div>
        <div
            v-if="showDayOfMonthPicker"
            class="flex flex-col text-center gap-1"
        >
            <p class="text-sm text-default">Numéro du jour du mois</p>
            <DatePicker
                v-model="adapter.sliceDatepickerDate!.value"
                date-format="dd"
                :pt="pt"
                unstyled
                append-to="self"
                show-icon
                icon-display="input"
                :show-other-months="false"
            />
        </div>
        <div
            v-if="showMonthOfYearPicker"
            class="flex flex-col text-center gap-1"
        >
            <p class="text-sm text-default">Mois</p>
            <MonthOfYearPicker v-model="adapter.sliceDatepickerDate!.value" />
        </div>
        <div
            v-if="showDayMonthOfYearPicker"
            class="flex flex-col text-center gap-1"
        >
            <p class="text-sm text-default">Jour de l'année</p>
            <DatePicker
                v-model="adapter.sliceDatepickerDate!.value"
                date-format="dd/mm"
                :pt="ptDayMonthOfYear"
                unstyled
                append-to="self"
                show-icon
                icon-display="input"
                :show-other-months="false"
            />
        </div>
        <div
            v-if="showCalendarDayPicker"
            class="flex flex-col text-center gap-1"
        >
            <p class="text-sm text-default">Numéro du jour du mois</p>
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
        <div
            v-if="showCalendarMonthPicker"
            class="flex flex-col text-center gap-1"
        >
            <p class="text-sm text-default">Mois</p>
            <MonthOfYearPicker
                v-model="adapter.calendarDatepickerDate!.value"
            />
        </div>
    </div>
</template>
