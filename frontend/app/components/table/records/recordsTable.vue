<script setup lang="ts">
import { h } from "vue";
import { UBadge } from "#components";
import { storeToRefs } from "pinia";
import { useRecordsTableStore } from "~/stores/recordsTableStore";
import RecordsFilterBar from "~/components/table/records/RecordsFilterBar.vue";
import { buildRecordsCsv } from "~/utils/recordsCsv";
import {
    CENTERED_COL,
    EXPORT_BTN_UI,
    REGION_META,
    STATION_META,
    TEMPERATURE_BADGE_SIZE,
    makeSortableColFactory,
    temperatureBadgeClass,
    truncatedCell,
} from "~/constants/tableUtils";

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

const ordering = ref("");
function setOrdering(key: string) {
    if (ordering.value === key) ordering.value = `-${key}`;
    else if (ordering.value === `-${key}`) ordering.value = "";
    else ordering.value = key;
}

interface TableRow {
    name: string;
    departement: string;
    record: number;
    recordDate: string;
}

const rawTableData = computed<TableRow[]>(() =>
    pagedStations.value.map((s) => ({
        name: s.station_name,
        departement: s.department,
        record: s.record_value,
        recordDate: s.record_date,
    })),
);

const tableData = computed<TableRow[]>(() => {
    if (!ordering.value) return rawTableData.value;
    const desc = ordering.value.startsWith("-");
    const key = (
        desc ? ordering.value.slice(1) : ordering.value
    ) as keyof TableRow;
    const dir = desc ? -1 : 1;
    return [...rawTableData.value].sort((a, b) => {
        if (a[key] < b[key]) return -dir;
        if (a[key] > b[key]) return dir;
        return 0;
    });
});

const sortableCol = makeSortableColFactory<TableRow>(ordering, setOrdering);

const columns = [
    sortableCol("name", "Station", {
        meta: STATION_META,
        cellCustom: ({ row }) => truncatedCell(row.getValue("name")),
    }),
    sortableCol("departement", "Département", {
        meta: REGION_META,
        cellCustom: ({ row }) => truncatedCell(row.getValue("departement")),
    }),
    sortableCol("record", "Record", {
        meta: CENTERED_COL,
        cellCustom: ({ row }) =>
            h(
                UBadge,
                {
                    class: [
                        "capitalize",
                        temperatureBadgeClass(
                            temperatureBadgeColor.value === "error",
                        ),
                    ],
                    variant: "subtle",
                    size: TEMPERATURE_BADGE_SIZE,
                },
                () => `${row.getValue<number>("record").toFixed(1)} °C`,
            ),
    }),
    sortableCol("recordDate", "Date du record", { meta: CENTERED_COL }),
];
</script>

<template>
    <div class="flex flex-col gap-4">
        <div class="flex items-center gap-4">
            <RecordsFilterBar />
            <UButton
                label="Exporter CSV"
                icon="i-lucide-download"
                class="ml-auto"
                :ui="EXPORT_BTN_UI"
                :disabled="pending"
                @click="downloadCsv"
            />
        </div>

        <div v-if="error" class="px-4 py-3 bg-error/10 text-error rounded">
            Error loading stations: {{ error.message }}
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
                :total="filteredCount"
                :items-per-page="pageSize"
            />
        </div>
    </div>
</template>
