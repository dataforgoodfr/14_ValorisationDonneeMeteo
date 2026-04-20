<script setup lang="ts">
import type { TableColumn } from "@nuxt/ui";
import { h } from "vue";
import { UBadge } from "#components";
import { storeToRefs } from "pinia";
import { useRecordsTableStore } from "~/stores/recordsTableStore";
import RecordsFilterBar from "~/components/table/records/RecordsFilterBar.vue";
import { buildRecordsCsv } from "~/utils/recordsCsv";

const store = useRecordsTableStore();
const {
    page,
    pageSize,
    typeRecords,
    periodSelection,
    pagedStations,
    filteredRecords,
    filteredCount,
    pending,
    error,
} = storeToRefs(store);

function downloadCsv() {
    if (!import.meta.client) return;
    const csv = buildRecordsCsv(filteredRecords.value);
    const a = document.createElement("a");
    a.href = `data:text/csv;charset=utf-8,${encodeURIComponent(csv)}`;
    a.download = useFormatFileName(
        `tableau-records-${typeRecords.value}`,
        periodSelection.value,
        "csv",
    );
    a.click();
    a.remove();
}

// Track the record type that corresponds to the data currently displayed,
// so the badge color only flips once the new data has arrived.
const displayedTypeRecords = ref(typeRecords.value);
watch(pagedStations, () => {
    displayedTypeRecords.value = typeRecords.value;
});

const temperatureBadgeColor = computed(() =>
    displayedTypeRecords.value === "hot" ? "error" : "info",
);

interface TableRow {
    name: string;
    departement: string;
    record: number;
    recordDate: string;
}

const tableData = computed<TableRow[]>(() =>
    pagedStations.value.map((s) => ({
        name: s.station_name,
        departement: s.department,
        record: s.record_value,
        recordDate: s.record_date,
    })),
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
        <!-- Controls: Période + Chaud/Froid -->
        <div class="flex flex-wrap items-end gap-4">
            <div class="flex flex-col gap-1">
                <p class="text-sm text-muted">Période</p>
                <USelect v-model="periodSelection" :items="periodOptions" />
            </div>
            <UButtonGroup>
                <UButton
                    color="neutral"
                    :variant="typeRecords === 'hot' ? 'subtle' : 'outline'"
                    label="Chaud"
                    @click="typeRecords = 'hot'"
                />
                <UButton
                    color="neutral"
                    :variant="typeRecords === 'cold' ? 'subtle' : 'outline'"
                    label="Froid"
                    @click="typeRecords = 'cold'"
                />
            </UButtonGroup>
            <UButton
                label="Exporter CSV"
                icon="i-lucide-download"
                color="neutral"
                :disabled="pending"
                @click="downloadCsv"
            />
        </div>

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
                :total="filteredCount"
                :items-per-page="pageSize"
            />
        </div>
    </div>
</template>
