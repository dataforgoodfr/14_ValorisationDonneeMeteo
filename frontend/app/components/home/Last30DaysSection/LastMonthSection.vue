<script setup lang="ts">
import type { TemperatureRecordsGraphParams, TypeRecords } from "~/types/api";
import ExtremeStationCard from "../ExtremeStationCard.vue";
import GoToDataLink from "../GoToDataLink.vue";
import Section from "../Section.vue";
import TemperatureRecord from "../TemperatureRecord.vue";

const { yesterday, yesterdayLess30Days } = useCustomDate();

function getYesterdayLastYear(yesterday: Date) {
    const yesterdayLastYear = yesterday;
    yesterdayLastYear.setFullYear(yesterdayLastYear.getFullYear() - 1);
    return yesterdayLastYear;
}

function getLastYearLast30Days(yesterday: Date) {
    const lastYearLast30Days = yesterday;
    lastYearLast30Days.setDate(lastYearLast30Days.getDate() - 30);
    return lastYearLast30Days;
}

const hotTypeRecords = ref<TypeRecords>("hot");
const coldTypeRecords = ref<TypeRecords>("cold");
const currentMonth = new Date().getMonth();

// This month records
const hotRecordsParams: TemperatureRecordsGraphParams = {
    type_records: hotTypeRecords.value,
    granularity: "month",
    month: currentMonth,
    date_start: dateToStringYMD(yesterdayLess30Days.value),
    date_end: dateToStringYMD(yesterday.value),
};
const { data: hotRecords } = useTemperatureRecordsGraph(hotRecordsParams);

const coldRecordsParams: TemperatureRecordsGraphParams = {
    type_records: coldTypeRecords.value,
    granularity: "month",
    month: currentMonth,
    date_start: dateToStringYMD(yesterdayLess30Days.value),
    date_end: dateToStringYMD(yesterday.value),
};
const { data: coldRecords } = useTemperatureRecordsGraph(coldRecordsParams);
const hotRecordsCount = computed(
    () => hotRecords.value?.buckets[0]?.nb_records_battus ?? 0,
);
const coldRecordsCount = computed(
    () => coldRecords.value?.buckets[0]?.nb_records_battus ?? 0,
);

// Last year month records
const yesterdayLastYear = getYesterdayLastYear(yesterday.value);
const lastYearLast30Days = getLastYearLast30Days(yesterdayLastYear);

const lastYearHotRecordsParams: TemperatureRecordsGraphParams = {
    type_records: hotTypeRecords.value,
    granularity: "month",
    month: currentMonth,
    date_start: dateToStringYMD(lastYearLast30Days),
    date_end: dateToStringYMD(yesterdayLastYear),
};
const { data: lastYearHotRecords } = useTemperatureRecordsGraph(
    lastYearHotRecordsParams,
);

const lastYearColdRecordsParams: TemperatureRecordsGraphParams = {
    type_records: coldTypeRecords.value,
    granularity: "month",
    month: currentMonth,
    date_start: dateToStringYMD(lastYearLast30Days),
    date_end: dateToStringYMD(yesterdayLastYear),
};
const { data: lastYearColdRecords } = useTemperatureRecordsGraph(
    lastYearColdRecordsParams,
);
const lastYearHotRecordsCount = computed(
    () => lastYearHotRecords.value?.buckets[0]?.nb_records_battus ?? 0,
);
const lastYearColdRecordsCount = computed(
    () => lastYearColdRecords.value?.buckets[0]?.nb_records_battus ?? 0,
);
</script>

<template>
    <div>
        <Section
            :title="`CES 30 DERNIERS JOURS -  ${formatDateLongForDisplay(yesterdayLess30Days)} au ${formatDateLongForDisplay(yesterday)}`"
        >
            <h2 class="text-blue-700 dark:text-primary pb-2">
                ECART DE TEMPERATURE A LA NORMALE
            </h2>
            <div class="flex flex-col w-fit gap-2 mt-2">
                <ExtremeStationCard type="hot" />
                <ExtremeStationCard type="cold" />
            </div>
            <GoToDataLink :data-url="'/ecart-normale'" />
            <div class="border-b to-slate-200" />
            <h2 class="text-blue-700 dark:text-primary pb-2 pt-1">
                RECORDS DE TEMPERATURE
            </h2>
            <div class="flex gap-2 md:flex-row flex-col">
                <TemperatureRecord
                    :records="hotRecordsCount"
                    :difference="hotRecordsCount - lastYearHotRecordsCount"
                    type="hot"
                    period="les 30 derniers jours"
                    title="Records de chaleur"
                    tooltip-text="Le nombre de records de chaleur battus sur le mois en cours"
                    compare-to="année dernière"
                />
                <TemperatureRecord
                    :records="coldRecordsCount"
                    :difference="coldRecordsCount - lastYearColdRecordsCount"
                    type="cold"
                    period="les 30 derniers jours"
                    title="Records de froid"
                    tooltip-text="Le nombre de records de froid battus sur le mois en cours"
                    compare-to="année dernière"
                />
            </div>
            <GoToDataLink :data-url="'/records'" />
        </Section>
    </div>
</template>
