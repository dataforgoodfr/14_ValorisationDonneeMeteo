<script setup lang="ts">
const model = defineModel<Date>({ required: true });

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
    header: { class: "hidden" },
    inputIconContainer: {
        class: "absolute inset-y-0 end-0 flex items-center pe-3 pointer-events-none",
    },
    inputIcon: { class: "shrink-0 text-dimmed size-4" },
    title: { class: "flex gap-1 text-sm font-medium text-highlighted" },
    selectMonth: {
        class: "hover:bg-elevated rounded px-1 py-0.5 cursor-pointer text-highlighted text-sm transition-colors",
    },
    selectYear: { class: "hidden" },
    monthView: { class: "grid grid-cols-3 gap-1 mt-1" },
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
};
</script>

<template>
    <DatePicker
        v-model="model"
        view="month"
        date-format="MM"
        :pt="pt"
        unstyled
        append-to="self"
        show-icon
        icon-display="input"
    />
</template>
