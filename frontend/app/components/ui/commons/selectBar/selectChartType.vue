<script setup lang="ts">
import type {
    ChartType,
    SelectBarAdapter,
} from "~/components/ui/commons/selectBar/types";

const adapter = inject<SelectBarAdapter>("selectBarAdapter")!;

const chartTypes = reactive([
    { label: "Bar Chart", value: "bar", icon: "i-lucide-chart-column" },
    { label: "Line Chart", value: "line", icon: "i-lucide-chart-line" },
]);
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
