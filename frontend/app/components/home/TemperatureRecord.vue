<script setup lang="ts">
import type { PeriodType } from "~/types/api";
import Card from "./Card.vue";

interface Props {
    period?: string;
    title: string;
    tooltipText: string;
    compareTo: string;
    type: "hot" | "cold";
    records: number;
    difference?: number;
    temperatureTitle?: string;
    exportButtonTitle?: string;
    periodType: "today" | "month";
    exportPeriodType: PeriodType;
}

const props = defineProps<Props>();
const { exportRecords } = useExportRecordsBattus();
const { yesterday, yesterdayLess30Days } = useCustomDate();

const arrowColor = computed(() => {
    if (props.difference === undefined || props.difference === 0) return "";
    const isUp = props.difference > 0;
    return (isUp && props.type === "hot") || (!isUp && props.type === "cold")
        ? "text-red-450"
        : "text-blue-600";
});

const exportCsvParams = computed(() => {
    const today = new Date();
    const dateStart =
        props.periodType === "today"
            ? dateToStringYMD(today)
            : dateToStringYMD(yesterdayLess30Days.value);
    const dateEnd =
        props.periodType === "today"
            ? dateToStringYMD(today)
            : dateToStringYMD(yesterday.value);

    return {
        dateStart,
        dateEnd,
    };
});

function exportInCsv() {
    const params = exportCsvParams.value;
    exportRecords(
        props.type,
        params.dateStart,
        params.dateEnd,
        props.exportPeriodType,
    );
}
</script>
<template>
    <div class="min-w-56">
        <Card
            :title="props.title"
            :tooltip-text="props.tooltipText"
            :export-button-title="props.exportButtonTitle"
            @export="exportInCsv"
        >
            <template #kpi>
                <span
                    class="text-4xl font-semibold"
                    :class="
                        props.type === 'hot' ? 'text-red-450' : 'text-blue-600'
                    "
                    >{{ props.records }}</span
                >
                <span
                    :class="
                        props.type === 'hot' ? 'text-red-450' : 'text-blue-600'
                    "
                >
                    records</span
                >
            </template>
            <template v-if="props.period" #kpi-context-text>
                {{ props.period }}
            </template>
            <template v-if="props.difference !== undefined" #variation>
                <UIcon
                    v-if="props.difference > 0"
                    :name="'i-lucide-arrow-up-right'"
                    :class="arrowColor"
                />
                <UIcon
                    v-if="props.difference < 0"
                    :name="'i-lucide-arrow-down-right'"
                    :class="arrowColor"
                />
                <span class="text-sm font-semibold" :class="arrowColor">
                    {{ props.difference !== 0 ? props.difference : "=" }}
                </span>
                <span class="text-sm"> vs. {{ props.compareTo }}</span>
            </template>
        </Card>
    </div>
</template>
