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
    })),
);

const { data: previousData } = useTemperatureRecordsGraph(
    computed(() => ({
        date_start: dateToStringYMD(yesterdayLastYearLess365Days.value),
        date_end: dateToStringYMD(yesterdayLastYear.value),
        granularity: "day",
        type_records: "all",
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
        title="Records de chaleur VS Records de froid"
        tooltip-text="Ratio entre les records de chaleur et les records de froid battus en France Métropolitaine sur les 365 derniers jours."
        :hot-value="hotCount"
        :cold-value="coldCount"
        :variation="variation"
        hot-label="chaleur"
        cold-label="froid"
    />
</template>
