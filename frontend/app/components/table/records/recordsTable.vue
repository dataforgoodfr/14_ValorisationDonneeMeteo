<script setup lang="ts">
import { h } from "vue";
import { UBadge, UButton } from "#components";
import { storeToRefs } from "pinia";
import { useRecordsTableStore } from "~/stores/recordsTableStore";
import {
    CENTERED_COL,
    REGION_META,
    STATION_META,
    TABLE_HEADER_BTN_MULTILINE_CLASS,
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
    filteredRecords,
    filteredCount,
    pending,
    error,
    ordering,
    hasActiveFilters,
} = storeToRefs(store);
const { resetFilters } = store;

// Track the record type that corresponds to the data currently displayed,
// so the badge color only flips once the new data has arrived.
const displayedTypeRecords = ref(typeRecords.value);
watch(filteredRecords, () => {
    displayedTypeRecords.value = typeRecords.value;
});

const temperatureBadgeColor = computed(() =>
    displayedTypeRecords.value === "hot" ? "error" : "info",
);

function setOrdering(key: string) {
    page.value = 1;
    if (ordering.value === key) ordering.value = `-${key}`;
    else if (ordering.value === `-${key}`) ordering.value = "";
    else ordering.value = key;
}

interface TableRow {
    name: string;
    departement: string;
    record: number;
    recordDate: string;
    classeRecente: number;
    anneeDeCreation: number;
    alt: number;
}

// Sort ALL filtered records before pagination so that ordering is global.
const sortedRecords = computed<TableRow[]>(() => {
    const all = filteredRecords.value.map((s) => ({
        name: s.station_name,
        departement: s.department,
        record: s.record_value,
        recordDate: s.record_date,
        classeRecente: s.classe_recente,
        anneeDeCreation: new Date(s.date_de_creation).getFullYear(),
        alt: s.alt,
    }));
    if (!ordering.value) return all;
    const desc = ordering.value.startsWith("-");
    const key = (
        desc ? ordering.value.slice(1) : ordering.value
    ) as keyof TableRow;
    const dir = desc ? -1 : 1;
    return [...all].sort((a, b) => {
        if (a[key] < b[key]) return -dir;
        if (a[key] > b[key]) return dir;
        return 0;
    });
});

const tableData = computed<TableRow[]>(() => {
    const start = (page.value - 1) * pageSize.value;
    return sortedRecords.value.slice(start, start + pageSize.value);
});

const sortableCol = makeSortableColFactory<TableRow>(ordering, setOrdering);

const columns = [
    sortableCol("name", "Station", {
        meta: STATION_META,
        cellCustom: ({ row }) => truncatedCell(row.getValue("name")),
    }),
    sortableCol("departement", "Dept.", {
        meta: REGION_META,
        cellCustom: ({ row }) => truncatedCell(row.getValue("departement")),
    }),
    sortableCol("record", "Température du record absolu", {
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
    sortableCol("recordDate", "Date du record absolu", {
        meta: CENTERED_COL,
    }),
    sortableCol("classeRecente", "Classe", { meta: CENTERED_COL }),
    sortableCol("alt", "Alt.", {
        meta: CENTERED_COL,
        cellCustom: ({ row }) => h(() => `${row.getValue<number>("alt")} m`),
    }),
    sortableCol("anneeDeCreation", "Année de création", {
        meta: CENTERED_COL,
        headerCustom: () =>
            h(
                UButton,
                {
                    variant: "ghost",
                    trailingIcon: ordering.value.includes("anneeDeCreation")
                        ? ordering.value.startsWith("-")
                            ? "i-lucide-arrow-down"
                            : "i-lucide-arrow-up"
                        : "i-lucide-arrow-up-down",
                    color: "neutral",
                    class: TABLE_HEADER_BTN_MULTILINE_CLASS,
                    onClick: () => setOrdering("anneeDeCreation"),
                },
                () =>
                    h(
                        "span",
                        { class: "whitespace-pre-line" },
                        "Année\nde création",
                    ),
            ),
    }),
];
</script>

<template>
    <div class="flex flex-col gap-4 w-full overflow-x-auto">
        <div v-if="error" class="px-4 py-3 bg-error/10 text-error rounded">
            Error loading stations: {{ error.message }}
        </div>

        <UTable
            :data="tableData"
            :columns="columns"
            :loading="pending"
            loading-color="primary"
            loading-animation="carousel"
            class="flex-1"
        >
            <template #loading>
                <tr v-for="i in 5" :key="i">
                    <td
                        v-for="(_, colIndex) in columns"
                        :key="colIndex"
                        class="px-4 py-3"
                    >
                        <USkeleton class="h-4 w-full" />
                    </td>
                </tr>
            </template>
            <template #empty>
                <TableEmptyState
                    :has-active-filters="hasActiveFilters"
                    @reset="resetFilters"
                />
            </template>
        </UTable>

        <div class="flex justify-center border-t border-accented pt-4">
            <UPagination
                v-model:page="page"
                :total="filteredCount"
                :items-per-page="pageSize"
            />
        </div>
    </div>
</template>
