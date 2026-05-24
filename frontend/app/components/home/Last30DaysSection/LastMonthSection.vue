<script setup lang="ts">
import type { TemperatureRecordsGraphParams, TypeRecords } from "~/types/api";
import GoToDataLink from "../GoToDataLink.vue";
import DeviationKpiPanel from "~/components/charts/DeviationKpiPanel.vue";
import Section from "../Section.vue";
import TemperatureRecord from "../TemperatureRecord.vue";
import HomeDeviationMap from "./HomeDeviationMap.vue";

const { yesterday, yesterdayLess30Days } = useCustomDate();

const dateStart = computed(() => dateToStringYMD(yesterdayLess30Days.value));
const dateEnd = computed(() => dateToStringYMD(yesterday.value));

function getYesterdayLastYear(yesterday: Date): Date {
    const yesterdayLastYear = new Date(yesterday);
    yesterdayLastYear.setFullYear(yesterdayLastYear.getFullYear() - 1);
    return yesterdayLastYear;
}

function getLastYearLast30Days(yesterday: Date): Date {
    const lastYearLast30Days = new Date(yesterday);
    lastYearLast30Days.setDate(lastYearLast30Days.getDate() - 30);
    return lastYearLast30Days;
}

const hotTypeRecords = ref<TypeRecords>("hot");
const coldTypeRecords = ref<TypeRecords>("cold");

// This month records
const hotRecordsParams = computed<TemperatureRecordsGraphParams>(() => ({
    type_records: hotTypeRecords.value,
    granularity: "day",
    date_start: dateToStringYMD(yesterdayLess30Days.value),
    date_end: dateToStringYMD(yesterday.value),
    period_type: "month",
}));
const { data: hotRecords } = useTemperatureRecordsGraph(hotRecordsParams);

const coldRecordsParams = computed<TemperatureRecordsGraphParams>(() => ({
    type_records: coldTypeRecords.value,
    granularity: "day",
    date_start: dateToStringYMD(yesterdayLess30Days.value),
    date_end: dateToStringYMD(yesterday.value),
    period_type: "month",
}));
const { data: coldRecords } = useTemperatureRecordsGraph(coldRecordsParams);
const hotRecordsCount = computed(
    () =>
        hotRecords.value?.buckets
            .map((bucket) => bucket.nb_records_battus)
            .reduce((a, b) => a + b, 0) ?? 0,
);
const coldRecordsCount = computed(
    () =>
        coldRecords.value?.buckets
            .map((bucket) => bucket.nb_records_battus)
            .reduce((a, b) => a + b, 0) ?? 0,
);

// Last year month records
const yesterdayLastYear = getYesterdayLastYear(yesterday.value);
const lastYearLast30Days = getLastYearLast30Days(yesterdayLastYear);

const lastYearHotRecordsParams = computed<TemperatureRecordsGraphParams>(
    () => ({
        type_records: hotTypeRecords.value,
        granularity: "day",
        date_start: dateToStringYMD(lastYearLast30Days),
        date_end: dateToStringYMD(yesterdayLastYear),
        period_type: "month",
    }),
);
const { data: lastYearHotRecords } = useTemperatureRecordsGraph(
    lastYearHotRecordsParams,
);

const lastYearColdRecordsParams = computed<TemperatureRecordsGraphParams>(
    () => ({
        type_records: coldTypeRecords.value,
        granularity: "day",
        date_start: dateToStringYMD(lastYearLast30Days),
        date_end: dateToStringYMD(yesterdayLastYear),
        period_type: "month",
    }),
);
const { data: lastYearColdRecords } = useTemperatureRecordsGraph(
    lastYearColdRecordsParams,
);
const lastYearHotRecordsCount = computed(
    () =>
        lastYearHotRecords.value?.buckets
            .map((bucket) => bucket.nb_records_battus)
            .reduce((a, b) => a + b, 0) ?? 0,
);
const lastYearColdRecordsCount = computed(
    () =>
        lastYearColdRecords.value?.buckets
            .map((bucket) => bucket.nb_records_battus)
            .reduce((a, b) => a + b, 0) ?? 0,
);
</script>

<template>
    <Section
        :title="`CES 30 DERNIERS JOURS -  ${formatDateLongForDisplay(yesterdayLess30Days)} au ${formatDateLongForDisplay(yesterday)}`"
    >
        <h2 class="text-blue-700 dark:text-primary pb-0">
            ECART DE TEMPÉRATURE A LA NORMALE
        </h2>
        <div class="flex flex-col lg:flex-row gap-4 mt-0 mb-4 lg:items-start">
            <HomeDeviationMap
                :date-start="dateStart"
                :date-end="dateEnd"
                class="w-full max-w-sm lg:flex-1 lg:max-w-none"
            />
            <div class="flex flex-col gap-3 flex-1 min-w-0">
                <DeviationKpiPanel
                    :date-start="dateStart"
                    :date-end="dateEnd"
                    compact
                />
                <GoToDataLink
                    :data-url="'/temperature/ecart-normale?preset=30d#table'"
                />
            </div>
        </div>
        <div class="border-b to-slate-200" />
        <h2 class="text-blue-700 dark:text-primary pb-2 pt-1">
            RECORDS DE TEMPÉRATURE MENSUELS
        </h2>
        <div class="flex gap-2 md:flex-row flex-col">
            <TemperatureRecord
                :records="hotRecordsCount"
                :difference="hotRecordsCount - lastYearHotRecordsCount"
                type="hot"
                period="ces 30 derniers jours"
                title="Records de chaleur mensuels"
                tooltip-text="Nombre de stations ayant battu un record de chaleur mensuel au cours des 30 derniers jours"
                compare-to="année dernière"
                export-button-title="Exporter la liste des records de chaleur"
                period-type="month"
                export-period-type="month"
            />
            <TemperatureRecord
                :records="coldRecordsCount"
                :difference="coldRecordsCount - lastYearColdRecordsCount"
                type="cold"
                period="les 30 derniers jours"
                title="Records de froid mensuels"
                tooltip-text="Nombre de stations ayant battu un record de froid mensuel au cours des 30 derniers jours"
                compare-to="année dernière"
                export-button-title="Exporter la liste des records de froid"
                period-type="month"
                export-period-type="month"
            />
        </div>
        <div class="flex justify-end">
            <GoToDataLink
                :data-url="'/temperature/records?preset=30d&view=scatter#chart'"
            />
        </div>
    </Section>
</template>
