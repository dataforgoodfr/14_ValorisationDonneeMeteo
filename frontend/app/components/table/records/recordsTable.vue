<script setup lang="ts">
import type { TableColumn } from "@nuxt/ui";
import { h } from "vue";
import type { TemperatureRecord } from "~/types/api";
import { UBadge } from "#components";
import { storeToRefs } from "pinia";
import { useRecordsStore } from "~/stores/recordsStore";
import RecordsFilterBar from "~/components/ui/records/RecordsFilterBar.vue";

const store = useRecordsStore();
const { recordType, page, pageSize, recordsData, pending, error } =
    storeToRefs(store);

// Track the record type that corresponds to the data currently displayed,
// so the badge color only flips once the new data has arrived.
const displayedRecordType = ref(recordType.value);
watch(recordsData, () => {
    displayedRecordType.value = recordType.value;
});

const temperatureBadgeColor = computed(() =>
    displayedRecordType.value === "Chaud" ? "error" : "info",
);

const columns = computed<TableColumn<TemperatureRecord>[]>(() => [
    { accessorKey: "name", header: "Station" },
    { accessorKey: "ville", header: "Ville" },
    { accessorKey: "departement", header: "Département" },
    { accessorKey: "date_creation", header: "Date création" },
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
    { accessorKey: "record_date", header: "Date du record" },
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
            :data="recordsData?.stations || []"
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
