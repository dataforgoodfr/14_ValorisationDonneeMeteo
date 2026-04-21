<script setup lang="ts">
import MonthOfYearPicker from "./monthOfYearPicker.vue";
import type { SelectBarAdapter } from "~/components/ui/commons/selectBar/types";

const adapter = inject<SelectBarAdapter>("selectBarAdapter")!;

const periodTypeOptions = [
    { label: "Période complète", value: "all_time" },
    { label: "Saison", value: "season" },
    { label: "Mois", value: "month" },
];

const seasonOptions = [
    { label: "Printemps", value: "spring" },
    { label: "Été", value: "summer" },
    { label: "Automne", value: "autumn" },
    { label: "Hiver", value: "winter" },
];

const monthDate = computed({
    get: () => new Date(2000, (adapter.month?.value ?? 1) - 1, 1),
    set: (date: Date) => {
        if (adapter.month) adapter.month.value = date.getMonth() + 1;
    },
});
</script>

<template>
    <div class="flex gap-6">
        <div class="flex flex-col text-center gap-1">
            <p class="text-sm text-default">Période</p>
            <USelect
                v-model="adapter.periodType!.value"
                :items="periodTypeOptions"
            />
        </div>
        <div
            v-if="adapter.periodType?.value === 'season'"
            class="flex flex-col text-center gap-1"
        >
            <p class="text-sm text-default">Saison</p>
            <USelect
                v-model="adapter.season!.value"
                :items="seasonOptions"
                placeholder="Choisir"
            />
        </div>
        <div
            v-if="adapter.periodType?.value === 'month'"
            class="flex flex-col text-center gap-1"
        >
            <p class="text-sm text-default">Mois</p>
            <MonthOfYearPicker v-model="monthDate" />
        </div>
    </div>
</template>
