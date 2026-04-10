<script setup lang="ts">
import type { TableColumn } from "@nuxt/ui";
import { h } from "vue";
import { UBadge } from "#components";
import { storeToRefs } from "pinia";
import { useDeviationTableStore } from "~/stores/deviationTableStore";
import DeviationFilterBar from "~/components/table/deviation/DeviationFilterBar.vue";

const store = useDeviationTableStore();
const { page, pageSize, data, pending, error } = storeToRefs(store);

interface TableRow {
    station_name: string;
    departement: string;
    deviation: number;
}

const tableData = computed<TableRow[]>(() =>
    (data.value?.results ?? []).map((r) => ({
        station_name: r.station_name,
        departement: r.departement,
        deviation: r.deviation,
    })),
);

const deviationBadgeColor = (deviation: number) =>
    deviation >= 0 ? "error" : "info";

const columns: TableColumn<TableRow>[] = [
    { accessorKey: "station_name", header: "Station" },
    { accessorKey: "departement", header: "Département" },
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
];
</script>

<template>
    <div class="flex flex-col gap-4">
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
                :total="data?.count ?? 0"
                :items-per-page="pageSize"
            />
        </div>
    </div>
</template>
