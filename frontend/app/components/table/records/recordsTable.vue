<script setup lang="ts">
import type { TableColumn } from "@nuxt/ui";
import { h } from "vue";
import { UBadge } from "#components";
import { storeToRefs } from "pinia";
import { useRecordsTableStore } from "~/stores/recordsTableStore";
import RecordsFilterBar from "~/components/table/records/RecordsFilterBar.vue";

const store = useRecordsTableStore();
const { page, pageSize, typeRecords, recordsData, pending, error } =
    storeToRefs(store);

// Track the record type that corresponds to the data currently displayed,
// so the badge color only flips once the new data has arrived.
const displayedTypeRecords = ref(typeRecords.value);
watch(recordsData, () => {
    displayedTypeRecords.value = typeRecords.value;
});

const temperatureBadgeColor = computed(() =>
    displayedTypeRecords.value === "hot" ? "error" : "info",
);

// station_ids and departments in the metadata are parallel arrays
// zip them to derive the department for each station.
const stationDeptMap = computed(() => {
    const { station_ids = [], departments = [] } =
        recordsData.value?.metadata ?? {};
    return new Map(station_ids.map((id, i) => [id, departments[i]]));
});

interface TableRow {
    name: string;
    departement: string | undefined;
    record: number | undefined;
    recordDate: string | undefined;
}

const tableData = computed<TableRow[]>(() =>
    (recordsData.value?.stations ?? []).map((s) => {
        const record =
            displayedTypeRecords.value === "cold"
                ? s.cold_records[0]
                : s.hot_records[0];
        return {
            name: s.name,
            departement: stationDeptMap.value.get(s.id),
            record: record?.value,
            recordDate: record?.date,
        };
    }),
);

const columns = computed<TableColumn<TableRow>[]>(() => [
    { accessorKey: "name", header: "Station" },
    { accessorKey: "departement", header: "Département" },
    {
        accessorKey: "record",
        header: "Record",
        cell: ({ row }) =>
            h(
                UBadge,
                {
                    class: "capitalize",
                    variant: "subtle",
                    color: temperatureBadgeColor.value,
                },
                () => row.getValue("record"),
            ),
    },
    { accessorKey: "recordDate", header: "Date du record" },
]);
</script>

<template>
    <div class="flex flex-col gap-4">
        <!-- Filter bar -->
        <RecordsFilterBar />

        <!-- Error message -->
        <div v-if="error" class="px-4 py-3 bg-error/10 text-error rounded">
            Error loading stations: {{ error.message }}
        </div>

        <!-- Table -->
        <UTable
            :data="tableData"
            :columns="columns"
            :loading="pending"
            class="flex-1"
        />

        <!-- Pagination -->
        <div class="flex justify-center border-t border-accented pt-4">
            <UPagination
                v-model:page="page"
                :total="recordsData?.count ?? 0"
                :items-per-page="pageSize"
            />
        </div>
    </div>
</template>
