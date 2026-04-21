<script setup lang="ts">
import type { SelectBarAdapter } from "~/components/ui/commons/selectBar/types";
import type { TemperatureRecordsGraphResponse } from "~/types/api";
import RecordsScatterChart from "./recordsCharts/recordsScatterChart.vue";
import RecordsPyramidChart from "./recordsCharts/recordsPyramidChart.vue";

interface Props {
    adapter: SelectBarAdapter<TemperatureRecordsGraphResponse>;
}

const props = defineProps<Props>();
</script>

<template>
    <RecordsPyramidChart
        v-if="props.adapter.chartType?.value === 'pyramid'"
        :adapter="props.adapter"
    />
    <RecordsScatterChart v-else :adapter="props.adapter" />
</template>
