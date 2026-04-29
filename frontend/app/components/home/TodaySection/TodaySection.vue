<script setup lang="ts">
import type { TemperatureRecordsGraphParams, TypeRecords } from "~/types/api";
import GoToDataLink from "../GoToDataLink.vue";
import ITNCard from "../ImportantInformationSection/ITNCard.vue";
import Section from "../Section.vue";
import TemperatureRecord from "../TemperatureRecord.vue";

const { today, yesterday } = useCustomDate();

const hotTypeRecords = ref<TypeRecords>("hot");
const coldTypeRecords = ref<TypeRecords>("cold");

// Today records
const hotRecordsParams: TemperatureRecordsGraphParams = {
    type_records: hotTypeRecords.value,
    granularity: "day",
    date_start: dateToStringYMD(today.value),
    date_end: dateToStringYMD(today.value),
    period_type: "month",
};
const { data: hotRecords } = useTemperatureRecordsGraph(hotRecordsParams);

const coldRecordsParams: TemperatureRecordsGraphParams = {
    type_records: coldTypeRecords.value,
    granularity: "day",
    date_start: dateToStringYMD(today.value),
    date_end: dateToStringYMD(today.value),
    period_type: "month",
};
const { data: coldRecords } = useTemperatureRecordsGraph(coldRecordsParams);
const hotRecordsCount = computed(
    () => hotRecords.value?.buckets[0]?.nb_records_battus ?? 0,
);
const coldRecordsCount = computed(
    () => coldRecords.value?.buckets[0]?.nb_records_battus ?? 0,
);

// Yesterday records
const yesterdayHotRecordsParams: TemperatureRecordsGraphParams = {
    type_records: hotTypeRecords.value,
    granularity: "day",
    date_start: dateToStringYMD(yesterday.value),
    date_end: dateToStringYMD(yesterday.value),
    period_type: "month",
};
const { data: yesterdayHotRecords } = useTemperatureRecordsGraph(
    yesterdayHotRecordsParams,
);

const yesterdayColdRecordsParams: TemperatureRecordsGraphParams = {
    type_records: coldTypeRecords.value,
    granularity: "day",
    date_start: dateToStringYMD(yesterday.value),
    date_end: dateToStringYMD(yesterday.value),
    period_type: "month",
};
const { data: yesterdayColdRecords } = useTemperatureRecordsGraph(
    yesterdayColdRecordsParams,
);
const yesterdayHotRecordsCount = computed(
    () => yesterdayHotRecords.value?.buckets[0]?.nb_records_battus ?? 0,
);
const yesterdayColdRecordsCount = computed(
    () => yesterdayColdRecords.value?.buckets[0]?.nb_records_battus ?? 0,
);
</script>
<template>
    <div>
        <Section :title="`AUJOURD'HUI - ${formatDateLongForDisplay(today)}`">
            <h2 class="text-blue-700 pb-2 dark:text-primary">
                MIN-MAX DU JOUR
            </h2>
            <div class="flex flex-col gap-2">
                <ITNCard />
                <ITNCard />
            </div>
            <GoToDataLink :data-url="'/itn'" />

            <div class="border-b to-slate-200" />

            <h2 class="text-blue-700 dark:text-primary pb-2 pt-1">
                RECORDS DE TEMPERATURE
            </h2>
            <div class="flex gap-2 md:flex-row flex-col">
                <TemperatureRecord
                    :records="hotRecordsCount"
                    :difference="hotRecordsCount - yesterdayHotRecordsCount"
                    type="hot"
                    title="Records de chaleur"
                    tooltip-text="Le nombre de records de chaleur battus aujourd'hui"
                    compare-to="hier"
                />
                <TemperatureRecord
                    :records="coldRecordsCount"
                    :difference="coldRecordsCount - yesterdayColdRecordsCount"
                    type="cold"
                    title="Records de froid"
                    tooltip-text="Le nombre de records de froid battus aujourd'hui"
                    compare-to="hier"
                />
            </div>
            <GoToDataLink :data-url="'/records'" />
        </Section>
    </div>
</template>
<style lang="css" scoped></style>
