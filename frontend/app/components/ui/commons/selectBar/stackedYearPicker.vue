<script setup lang="ts">
import type { SelectBarAdapter } from "~/components/ui/commons/selectBar/types";

const adapter = inject<SelectBarAdapter>("selectBarAdapter")!;

const currentYear = new Date().getFullYear();
const MIN_YEAR = 1946;

const allYears = Array.from(
    { length: currentYear - MIN_YEAR + 1 },
    (_, i) => currentYear - i,
);

const selectedYears = adapter.selectedYears!;

function toggleYear(year: number) {
    const idx = selectedYears.value.indexOf(year);
    if (idx === -1) {
        selectedYears.value = [...selectedYears.value, year].sort(
            (a, b) => a - b,
        );
    } else {
        selectedYears.value = selectedYears.value.filter((y) => y !== year);
    }
}

const label = computed(() => {
    if (selectedYears.value.length === 0) return "Aucune année";
    return selectedYears.value
        .slice()
        .sort((a, b) => a - b)
        .join(", ");
});
</script>

<template>
    <UFormField label="Années" name="stacked-years">
        <UPopover :content="{ align: 'start' }">
            <UButton
                color="neutral"
                variant="outline"
                trailing-icon="i-lucide-chevron-down"
                class="min-w-32 max-w-64 truncate"
            >
                {{ label }}
            </UButton>
            <template #content>
                <div
                    class="flex flex-col max-h-72 overflow-y-auto p-1 min-w-28"
                >
                    <label
                        v-for="year in allYears"
                        :key="year"
                        class="flex items-center gap-2 px-2 py-1 rounded hover:bg-elevated cursor-pointer select-none text-sm"
                    >
                        <input
                            type="checkbox"
                            :checked="selectedYears.includes(year)"
                            class="accent-primary"
                            @change="toggleYear(year)"
                        />
                        {{ year }}
                    </label>
                </div>
            </template>
        </UPopover>
    </UFormField>
</template>
