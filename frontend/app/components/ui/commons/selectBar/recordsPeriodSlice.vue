<script setup lang="ts">
import type { Season } from "~/types/api";
import type { SelectBarAdapter } from "~/components/ui/commons/selectBar/types";
import { MONTH_LONG } from "~/constants/months";

const adapter = inject<SelectBarAdapter>("selectBarAdapter")!;

const periodTypeOptions = [
    { label: "Annuel", value: "all_time" },
    { label: "Saisonnier", value: "season" },
    { label: "Mensuel", value: "month" },
];

const seasonOptions = [
    { label: "Toutes les saisons", value: "all" },
    { label: "Printemps", value: "spring" },
    { label: "Été", value: "summer" },
    { label: "Automne", value: "autumn" },
    { label: "Hiver", value: "winter" },
];

const monthOptions = [
    { label: "Tous les mois", value: 0 },
    ...MONTH_LONG.map((label, i) => ({ label, value: i + 1 })),
];

const seasonDisplayValue = computed({
    get: () => adapter.season?.value ?? "all",
    set: (val: string) => {
        if (adapter.season) {
            adapter.season.value = val === "all" ? undefined : (val as Season);
        }
    },
});

const monthDisplayValue = computed({
    get: () => adapter.month?.value ?? 0,
    set: (val: number) => {
        if (adapter.month) {
            adapter.month.value = val === 0 ? undefined : val;
        }
    },
});
</script>

<template>
    <div class="flex gap-6">
        <div class="flex flex-col text-center gap-1">
            <p class="text-sm text-default">Type de records</p>
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
            <USelect v-model="seasonDisplayValue" :items="seasonOptions" />
        </div>
        <div
            v-if="adapter.periodType?.value === 'month'"
            class="flex flex-col text-center gap-1"
        >
            <p class="text-sm text-default">Mois</p>
            <USelect v-model="monthDisplayValue" :items="monthOptions" />
        </div>
    </div>
</template>
