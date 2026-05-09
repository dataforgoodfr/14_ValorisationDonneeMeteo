<script setup lang="ts">
import type { TemperatureRecordsGraphParams, TypeRecords } from "~/types/api";
import GoToDataLink from "../GoToDataLink.vue";
import Section from "../Section.vue";
import TemperatureRecord from "../TemperatureRecord.vue";
// import ExtremeCard from "../ExtremeCard.vue";

const { today, lastYear } = useCustomDate();

const hotTypeRecords = ref<TypeRecords>("hot");
const coldTypeRecords = ref<TypeRecords>("cold");

const hotRecordsParams = computed<TemperatureRecordsGraphParams>(() => ({
    type_records: hotTypeRecords.value,
    granularity: "day",
    date_start: dateToStringYMD(today.value),
    date_end: dateToStringYMD(today.value),
    period_type: "month",
}));
const { data: hotRecords } = useTemperatureRecordsGraph(hotRecordsParams);

const coldRecordsParams = computed<TemperatureRecordsGraphParams>(() => ({
    type_records: coldTypeRecords.value,
    granularity: "day",
    date_start: dateToStringYMD(today.value),
    date_end: dateToStringYMD(today.value),
    period_type: "month",
}));
const { data: coldRecords } = useTemperatureRecordsGraph(coldRecordsParams);
const hotRecordsCount = computed(
    () => hotRecords.value?.buckets[0]?.nb_records_battus ?? 0,
);
const coldRecordsCount = computed(
    () => coldRecords.value?.buckets[0]?.nb_records_battus ?? 0,
);

const lastYearHotRecordsParams = computed<TemperatureRecordsGraphParams>(
    () => ({
        type_records: hotTypeRecords.value,
        granularity: "day",
        date_start: dateToStringYMD(lastYear.value),
        date_end: dateToStringYMD(lastYear.value),
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
        date_start: dateToStringYMD(lastYear.value),
        date_end: dateToStringYMD(lastYear.value),
        period_type: "month",
    }),
);
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
    <Section :title="`AUJOURD'HUI - ${formatDateLongForDisplay(today)}`">
        <!-- Commenter jusqu'à ce que ca soit dispo -->
        <!-- <h2 class="text-blue-700 pb-2 dark:text-primary">
                MIN-MAX DU JOUR
            </h2>
            <div class="flex flex-col gap-2">
                <ExtremeCard hot-cold="hot" :disabled="true" />
                <ExtremeCard hot-cold="cold" :disabled="true" />
            </div>
            <GoToDataLink :data-url="'/itn'" />

            <div class="border-b to-slate-200" /> -->

        <h2 class="text-blue-700 dark:text-primary pb-2 pt-1">
            RECORDS DE TEMPÉRATURE MENSUELS
        </h2>
        <div class="flex gap-2 md:flex-row flex-col">
            <TemperatureRecord
                :records="hotRecordsCount"
                :difference="hotRecordsCount - lastYearHotRecordsCount"
                type="hot"
                title="Records de chaleur mensuels"
                tooltip-text="Nombre de stations ayant battu un record mensuel de chaleur aujourd'hui"
                compare-to="même jour l'an dernier"
            />
            <TemperatureRecord
                :records="coldRecordsCount"
                :difference="coldRecordsCount - lastYearColdRecordsCount"
                type="cold"
                title="Records de froid mensuels"
                tooltip-text="Nombre de stations ayant battu un record mensuel de froid aujourd'hui"
                compare-to="même jour l'an dernier"
            />
        </div>
        <GoToDataLink :data-url="'/records?preset=today#table'" />
    </Section>
</template>
