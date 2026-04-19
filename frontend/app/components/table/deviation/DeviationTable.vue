<script setup lang="ts">
import type { TableColumn } from "@nuxt/ui";
import { h } from "vue";
import { UBadge, UButton } from "#components";
import { storeToRefs } from "pinia";
import { useDeviationTableStore } from "~/stores/deviationTableStore";
import DeviationFilterBar from "~/components/table/deviation/DeviationFilterBar.vue";
import DayPicker from "~/components/ui/commons/selectBar/dayPicker.vue";
import { useCustomDate } from "~/composables/useCustomDate";
import type { TemperatureDeviationResponse } from "~/types/api";
import { buildDeviationCsv } from "~/utils/deviationCsv";
const store = useDeviationTableStore();

const dates = useCustomDate();
provide("selectBarAdapter", { maxDate: dates.yesterday });
const {
    page,
    pageSize,
    deviationData,
    exportParams,
    pending,
    error,
    dateStart,
    dateEnd,
    ordering,
} = storeToRefs(store);

const { apiFetch } = useApiClient();

async function downloadCsv() {
    if (!import.meta.client) return;
    const data = await apiFetch<TemperatureDeviationResponse>(
        "/temperature/deviation",
        { query: exportParams.value },
    );
    const csv = buildDeviationCsv(data.stations);
    const a = document.createElement("a");
    a.href = `data:text/csv;charset=utf-8,${encodeURIComponent(csv)}`;
    a.download = useFormatFileName(
        "tableau-ecart-normale",
        "", // non utile pour deviation
        "csv",
        dateStart.value,
        dateEnd.value,
    );
    a.click();
}
const { setOrdering } = store;

interface TableRow {
    station_name: string;
    departement: string | undefined;
    region: string | undefined;
    // altitude: number | undefined;
    deviation: number | undefined;
    temperatureMean: number | undefined;
}

const tableData = computed<TableRow[]>(() =>
    (deviationData.value?.stations ?? []).map((s) => ({
        station_name: s.station_name,
        departement: s.department,
        region: s.region,
        // altitude: s.alt,
        deviation: s.deviation,
        temperatureMean: s.temperature_mean,
    })),
);

const deviationBadgeColor = (deviation: number) =>
    deviation >= 0 ? "error" : "info";

const columns: TableColumn<TableRow>[] = [
    {
        accessorKey: "station_name",
        header: () =>
            h(UButton, {
                variant: "ghost",
                label: "Station",
                title: "Station",
                trailingIcon: ordering.value.includes("station_name")
                    ? ordering.value.startsWith("-")
                        ? "i-lucide-arrow-down"
                        : "i-lucide-arrow-up"
                    : "i-lucide-arrow-up-down",
                color: "neutral",
                class: "-mx-2.5 font-semibold text-highlighted w-full justify-center",
                onClick: () => setOrdering("station_name"),
            }),
    },
    {
        accessorKey: "departement",
        header: () =>
            h(UButton, {
                variant: "ghost",
                label: "Département",
                title: "Département",
                trailingIcon: ordering.value.includes("departement")
                    ? ordering.value.startsWith("-")
                        ? "i-lucide-arrow-down"
                        : "i-lucide-arrow-up"
                    : "i-lucide-arrow-up-down",
                color: "neutral",
                class: "-mx-2.5 font-semibold text-highlighted w-full justify-center",
                onClick: () => setOrdering("departement"),
            }),
        meta: { class: { td: "text-center" } },
    },
    {
        accessorKey: "region",
        header: () =>
            h(UButton, {
                variant: "ghost",
                label: "Région",
                title: "Région",
                trailingIcon: ordering.value.includes("region")
                    ? ordering.value.startsWith("-")
                        ? "i-lucide-arrow-down"
                        : "i-lucide-arrow-up"
                    : "i-lucide-arrow-up-down",
                color: "neutral",
                class: "-mx-2.5 font-semibold text-highlighted w-full justify-center",
                onClick: () => setOrdering("region"),
            }),
        meta: { class: { td: "text-center" } },
    },
    // {
    //     accessorKey: "altitude",
    //     header: () =>
    //         h(UButton, {
    //             variant: "ghost",
    //             label: "Altitude (m)",
    //             title: "Altitude (m)",
    //             trailingIcon: ordering.value.includes("altitude")
    //                 ? ordering.value.startsWith("-")
    //                     ? "i-lucide-arrow-down"
    //                     : "i-lucide-arrow-up"
    //                 : "i-lucide-arrow-up-down",
    //             color: "neutral",
    //             class: "-mx-2.5 font-semibold text-highlighted w-full justify-center",
    //             onClick: () => setOrdering("alt"),
    //         }),
    //     meta: { class: { td: "text-center" } },
    //     cell: ({ row }) => `${row.getValue<number>("altitude")} m`,
    // },
    {
        accessorKey: "deviation",
        header: () =>
            h(UButton, {
                variant: "ghost",
                label: "Écart à la normale (°C)",
                title: "Écart à la normale (°C)",
                trailingIcon: ordering.value.includes("deviation")
                    ? ordering.value.startsWith("-")
                        ? "i-lucide-arrow-down"
                        : "i-lucide-arrow-up"
                    : "i-lucide-arrow-up-down",
                color: "neutral",
                class: "-mx-2.5 font-semibold text-highlighted w-full justify-center",
                onClick: () => setOrdering("deviation"),
            }),
        meta: { class: { td: "text-center" } },
        cell: ({ row }) =>
            h(
                UBadge,
                {
                    class: "capitalize",
                    variant: "subtle",
                    color: deviationBadgeColor(row.getValue("deviation")),
                },
                () => `${row.getValue<number>("deviation").toFixed(1)} °C`,
            ),
    },
    {
        accessorKey: "temperatureMean",
        header: () =>
            h(UButton, {
                variant: "ghost",
                label: "Température Moyenne (°C)",
                title: "Température Moyenne (°C)",
                trailingIcon: ordering.value.includes("temperatureMean")
                    ? ordering.value.startsWith("-")
                        ? "i-lucide-arrow-down"
                        : "i-lucide-arrow-up"
                    : "i-lucide-arrow-up-down",
                color: "neutral",
                class: "-mx-2.5 font-semibold text-highlighted w-full justify-center",
                onClick: () => setOrdering("temperature_mean"),
            }),
        meta: { class: { td: "text-center" } },
        cell: ({ row }) =>
            `${row.getValue<number>("temperatureMean").toFixed(1)}`,
    },
];
</script>

<template>
    <div class="flex flex-col gap-4">
        <div class="flex items-end justify-between gap-4">
            <DayPicker
                v-model:start-date="dateStart"
                v-model:end-date="dateEnd"
                :min-date="dates.absoluteMinDataDate.value"
                :max-date="dates.yesterday.value"
            />
            <UButton
                label="Exporter CSV"
                icon="i-lucide-download"
                color="neutral"
                :disabled="pending"
                @click="downloadCsv"
            />
        </div>

        <DeviationFilterBar />

        <div v-if="error" class="px-4 py-3 bg-error/10 text-error rounded">
            Erreur de chargement : {{ error }}
        </div>

        <UTable
            :data="tableData"
            :columns="columns"
            :loading="pending"
            class="flex-1"
        />

        <div class="flex justify-center border-t border-accented pt-4">
            <UPagination
                v-model:page="page"
                :total="deviationData?.pagination.total_count ?? 0"
                :items-per-page="pageSize"
            />
        </div>
    </div>
</template>
