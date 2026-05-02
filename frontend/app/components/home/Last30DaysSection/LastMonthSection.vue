<script setup lang="ts">
import type { TemperatureRecordsGraphParams, TypeRecords } from "~/types/api";
import GoToDataLink from "../GoToDataLink.vue";
import ExtremeCard from "../ExtremeCard.vue";
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

const { data: hotDeviationData, status: hotDeviationStatus } =
    useTemperatureDeviation(
        {
            date_start: dateToStringYMD(yesterdayLess30Days.value),
            date_end: dateToStringYMD(yesterday.value),
            ordering: "-deviation",
            limit: 1,
        },
        undefined,
        false,
    );
const { data: coldDeviationData, status: coldDeviationStatus } =
    useTemperatureDeviation(
        {
            date_start: dateToStringYMD(yesterdayLess30Days.value),
            date_end: dateToStringYMD(yesterday.value),
            ordering: "deviation",
            limit: 1,
        },
        undefined,
        false,
    );
const hotStation = computed(() => {
    return hotDeviationData.value?.stations[0] ?? null;
});
const coldStation = computed(
    () => coldDeviationData.value?.stations[0] ?? null,
);
function formatDeviation(d: number) {
    return (d >= 0 ? "+" : "") + d.toFixed(1);
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
    period_type: "month",
};
const { data: hotRecords } = useTemperatureRecordsGraph(hotRecordsParams);

const coldRecordsParams: TemperatureRecordsGraphParams = {
    type_records: coldTypeRecords.value,
    granularity: "month",
    month: currentMonth,
    date_start: dateToStringYMD(yesterdayLess30Days.value),
    date_end: dateToStringYMD(yesterday.value),
    period_type: "month",
};
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

const lastYearHotRecordsParams: TemperatureRecordsGraphParams = {
    type_records: hotTypeRecords.value,
    granularity: "month",
    month: currentMonth,
    date_start: dateToStringYMD(lastYearLast30Days),
    date_end: dateToStringYMD(yesterdayLastYear),
    period_type: "month",
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
    period_type: "month",
};
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
    <div>
        <Section
            :title="`CES 30 DERNIERS JOURS -  ${formatDateLongForDisplay(yesterdayLess30Days)} au ${formatDateLongForDisplay(yesterday)}`"
        >
            <h2 class="text-blue-700 dark:text-primary pb-2">
                ECART DE TEMPÉRATURE A LA NORMALE
            </h2>
            <div
                class="flex flex-col lg:flex-row gap-4 mt-2 mb-4 lg:items-start"
            >
                <HomeDeviationMap
                    :date-start="dateStart"
                    :date-end="dateEnd"
                    class="w-full max-w-sm lg:flex-1 lg:max-w-none"
                />
                <div class="flex flex-col gap-3 flex-1 min-w-0">
                    <p class="text-sm text-muted">
                        Stations avec écart le plus important
                    </p>
                    <ExtremeCard
                        hot-cold="hot"
                        :loading="hotDeviationStatus === 'pending'"
                        :temperature="
                            hotStation
                                ? formatDeviation(hotStation.deviation)
                                : undefined
                        "
                        :city="hotStation?.station_name"
                        :department-string="hotStation?.region"
                        :department-number="hotStation?.department"
                    />
                    <ExtremeCard
                        hot-cold="cold"
                        :loading="coldDeviationStatus === 'pending'"
                        :temperature="
                            coldStation
                                ? formatDeviation(coldStation.deviation)
                                : undefined
                        "
                        :city="coldStation?.station_name"
                        :department-string="coldStation?.region"
                        :department-number="coldStation?.department"
                    />
                    <GoToDataLink :data-url="'/ecart-normale'" />
                </div>
            </div>
            <div class="border-b to-slate-200" />
            <h2 class="text-blue-700 dark:text-primary pb-2 pt-1">
                RECORDS MENSUELS DE TEMPÉRATURE
            </h2>
            <div class="flex gap-2 md:flex-row flex-col">
                <TemperatureRecord
                    :records="hotRecordsCount"
                    :difference="hotRecordsCount - lastYearHotRecordsCount"
                    type="hot"
                    period="ces 30 derniers jours"
                    title="Records mensuels de chaleur"
                    tooltip-text="Nombre de stations ayant battu un record mensuel de chaleur au cours des 30 derniers jours"
                    compare-to="année dernière"
                />
                <TemperatureRecord
                    :records="coldRecordsCount"
                    :difference="coldRecordsCount - lastYearColdRecordsCount"
                    type="cold"
                    period="les 30 derniers jours"
                    title="Records mensuels de froid"
                    tooltip-text="Nombre de stations ayant battu un record mensuel de froid au cours des 30 derniers jours"
                    compare-to="année dernière"
                />
            </div>
            <GoToDataLink :data-url="'/records'" />
        </Section>
    </div>
</template>
