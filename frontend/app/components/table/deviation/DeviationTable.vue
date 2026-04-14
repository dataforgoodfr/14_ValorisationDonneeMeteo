<script setup lang="ts">
import type { TableColumn } from "@nuxt/ui";
import { h } from "vue";
import { UBadge } from "#components";
import { storeToRefs } from "pinia";
import { useDeviationTableStore } from "~/stores/deviationTableStore";
import DeviationFilterBar from "~/components/table/deviation/DeviationFilterBar.vue";
import DayPicker from "~/components/ui/commons/selectBar/dayPicker.vue";
import { useCustomDate } from "~/composables/useCustomDate";

const store = useDeviationTableStore();
const { page, pageSize, deviationData, pending, error, dateStart, dateEnd } =
    storeToRefs(store);

interface TableRow {
    station_name: string;
    departement: string | undefined;
    region: string | undefined;
    altitude: number | undefined;
    deviation: number | undefined;
    temperatureMean: number | undefined;
}

const tableData = computed<TableRow[]>(() =>
    (deviationData.value?.stations ?? []).map((s) => ({
        station_name: s.station_name,
        departement: s.department,
        region: s.region,
        altitude: s.alt,
        deviation: s.deviation,
        temperatureMean: s.temperature_mean,
    })),
);

const deviationBadgeColor = (deviation: number) =>
    deviation >= 0 ? "error" : "info";

const columns: TableColumn<TableRow>[] = [
    { accessorKey: "station_name", header: "Station" },
    { accessorKey: "departement", header: "Département" },
    { accessorKey: "region", header: "Région" },
    {
        accessorKey: "altitude",
        header: "Altitude (m)",
        cell: ({ row }) => `${row.getValue<number>("altitude")} m`,
    },
    {
        accessorKey: "deviation",
        header: "Écart à la normale (°C)",
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
        header: "Température Moyenne (°C)",
        cell: ({ row }) =>
            `${row.getValue<number>("temperatureMean").toFixed(1)}`,
    },
];

const dates = useCustomDate();
</script>

<template>
    <div class="flex flex-col gap-4">
        <DayPicker
            v-model:start-date="dateStart"
            v-model:end-date="dateEnd"
            :min-date="dates.absoluteMinDataDate.value"
            :max-date="dates.twoDaysAgo.value"
        />

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
