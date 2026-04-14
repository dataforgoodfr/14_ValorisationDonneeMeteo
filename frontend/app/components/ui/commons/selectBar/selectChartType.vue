<script setup lang="ts">
import type {
    ChartType,
    SelectBarAdapter,
} from "~/components/ui/commons/selectBar/types";

const adapter = inject<SelectBarAdapter>("selectBarAdapter")!;
<<<<<<< HEAD
const chartTypes = adapter.chartTypeOptions;
=======

const chartTypes = computed(
    () =>
        // chaque adapter fournit ses propres boutons via chartTypes
        adapter.chartTypes ?? [
            { label: "Bar Chart", value: "bar", icon: "i-lucide-chart-column" },
            { label: "Line Chart", value: "line", icon: "i-lucide-chart-line" },
        ],
);
>>>>>>> 93cda2a (add calendar graph from main branch (#290))
</script>

<template>
    <UFormField
        v-if="
            adapter.features.hasChartTypeSelector &&
            adapter.chartType &&
            adapter.setChartType
        "
        label="Format"
        name="chart-type"
    >
        <template v-for="item in chartTypes" :key="item.value">
            <UButton
                :icon="item.icon"
                size="md"
                color="neutral"
                :active="adapter.chartType.value === item.value"
                active-class="bg-primary text-inverted"
                :variant="
                    adapter.chartType.value === item.value ? 'solid' : 'outline'
                "
                @click="adapter.setChartType(item.value as ChartType)"
            />
        </template>
    </UFormField>
</template>
