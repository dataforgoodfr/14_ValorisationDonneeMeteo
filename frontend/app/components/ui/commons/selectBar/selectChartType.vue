<script setup lang="ts">
import type {
    ChartType,
    SelectBarAdapter,
} from "~/components/ui/commons/selectBar/types";

const adapter = inject<SelectBarAdapter>("selectBarAdapter")!;
const chartTypes = adapter.chartTypeOptions;
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
                :ui="{
                    base:
                        adapter.chartType.value === item.value
                            ? 'bg-blue-350 ring-1 ring-blue-350 text-white'
                            : 'bg-transparent ring-1 ring-blue-350 text-black dark:text-white',
                }"
                @click="adapter.setChartType(item.value as ChartType)"
            />
        </template>
    </UFormField>
</template>
