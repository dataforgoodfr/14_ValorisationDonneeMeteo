<script setup lang="ts">
import HotColdRatioCard from "~/components/home/HotColdRatioCard.vue";
import type { TemperatureRecordsGraphParams } from "~/types/api";

const { yesterday, yesterdayLess365Days, yesterdayLastYear } = useCustomDate();

const yesterdayLastYearLess365Days = computed(() => {
    const d = new Date(yesterdayLastYear.value);
    d.setDate(d.getDate() - 365);
    return d;
});

const { data } = useTemperatureRecordsGraph(
    computed<TemperatureRecordsGraphParams>(() => ({
        date_start: dateToStringYMD(yesterdayLess365Days.value),
        date_end: dateToStringYMD(yesterday.value),
        granularity: "day",
        type_records: "all",
        period_type: "month",
    })),
);

const { data: previousData, pending } = useTemperatureRecordsGraph(
    computed(() => ({
        date_start: dateToStringYMD(yesterdayLastYearLess365Days.value),
        date_end: dateToStringYMD(yesterdayLastYear.value),
        granularity: "day",
        type_records: "all",
        period_type: "month",
    })),
);

const hotCount = computed(
    () =>
        data.value?.records.filter((r) => r.type_records === "hot").length ?? 0,
);
const coldCount = computed(
    () =>
        data.value?.records.filter((r) => r.type_records === "cold").length ??
        0,
);

const hotPercent = computed(() => {
    const total = hotCount.value + coldCount.value;
    return total > 0 ? Math.round((hotCount.value / total) * 100) : 0;
});

const previousHotPercent = computed(() => {
    const records = previousData.value?.records ?? [];
    const hot = records.filter((r) => r.type_records === "hot").length;
    const total = records.length;
    return total > 0 ? Math.round((hot / total) * 100) : 0;
});

const variation = computed(() =>
    previousData.value
        ? hotPercent.value - previousHotPercent.value
        : undefined,
);
</script>

<template>
    <HotColdRatioCard
        title="Records mensuels de chaleur VS froid"
        tooltip-text="Proportion du nombre de records de chaleur mensuels par rapport aux records de froid mensuels battus en France Métropolitaine au cours des 365 derniers jours."
        :hot-value="hotCount"
        :cold-value="coldCount"
        :variation="variation"
        hot-label="chaleur"
        cold-label="froid"
        :pending="pending"
    />
</template>
