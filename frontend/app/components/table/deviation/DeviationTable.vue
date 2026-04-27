<script setup lang="ts">
import { h } from "vue";
import { UBadge, UButton } from "#components";
import {
    CENTERED_TD,
    EXPORT_BTN_UI,
    REGION_META,
    STATION_META,
    TABLE_HEADER_BTN_MULTILINE_CLASS,
    TEMPERATURE_BADGE_SIZE,
    makeSortableColFactory,
    temperatureBadgeClass,
    truncatedCell,
} from "~/constants/tableUtils";
import { storeToRefs } from "pinia";
import { useDeviationTableStore } from "~/stores/deviationTableStore";
import DeviationFilterBar from "~/components/table/deviation/DeviationFilterBar.vue";
import DayPicker from "~/components/ui/commons/selectBar/dayPicker.vue";
import { useCustomDate } from "~/composables/useCustomDate";
import type { TemperatureDeviationResponse } from "~/types/api";
import { buildDeviationCsv } from "~/utils/deviationCsv";

const props = withDefaults(defineProps<{ showFilters?: boolean }>(), {
    showFilters: true,
});

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
    department: string | undefined;
    region: string | undefined;
    deviation: number | undefined;
    temperatureMean: number | undefined;
}

const tableData = computed<TableRow[]>(() =>
    (deviationData.value?.stations ?? []).map((s) => ({
        station_name: s.station_name,
        department: s.department,
        region: s.region,
        deviation: s.deviation,
        temperatureMean: s.temperature_mean,
    })),
);

const deviationBadgeColor = (deviation: number) =>
    deviation >= 0 ? "error" : "info";

const sortableCol = makeSortableColFactory<TableRow>(ordering, setOrdering);

const columns = [
    sortableCol("station_name", "Station", {
        meta: STATION_META,
        cellCustom: ({ row }) => truncatedCell(row.getValue("station_name")),
    }),
    sortableCol("department", "Département", { meta: CENTERED_TD }),
    sortableCol("region", "Région", {
        meta: REGION_META,
        cellCustom: ({ row }) => truncatedCell(row.getValue("region")),
    }),
    sortableCol("deviation", "Écart à la normale", {
        meta: CENTERED_TD,
        headerCustom: () =>
            h(
                UButton,
                {
                    variant: "ghost",
                    trailingIcon: ordering.value.includes("deviation")
                        ? ordering.value.startsWith("-")
                            ? "i-lucide-arrow-down"
                            : "i-lucide-arrow-up"
                        : "i-lucide-arrow-up-down",
                    color: "neutral",
                    class: TABLE_HEADER_BTN_MULTILINE_CLASS,
                    onClick: () => setOrdering("deviation"),
                },
                () =>
                    h(
                        "span",
                        { class: "whitespace-pre-line" },
                        "Écart à la\nnormale",
                    ),
            ),
        cellCustom: ({ row }) =>
            h(
                UBadge,
                {
                    class: [
                        "capitalize",
                        temperatureBadgeClass(
                            deviationBadgeColor(row.getValue("deviation")) ===
                                "error",
                        ),
                    ],
                    variant: "subtle",
                    size: TEMPERATURE_BADGE_SIZE,
                },
                () =>
                    `${row.getValue<number>("deviation") > 0 ? "+" : ""}${row.getValue<number>("deviation").toFixed(1)} °C`,
            ),
    }),
    sortableCol("temperatureMean", "Température Moyenne", {
        sortKey: "temperature_mean",
        meta: CENTERED_TD,
        headerCustom: () =>
            h(
                UButton,
                {
                    variant: "ghost",
                    trailingIcon: ordering.value.includes("temperature_mean")
                        ? ordering.value.startsWith("-")
                            ? "i-lucide-arrow-down"
                            : "i-lucide-arrow-up"
                        : "i-lucide-arrow-up-down",
                    color: "neutral",
                    class: TABLE_HEADER_BTN_MULTILINE_CLASS,
                    onClick: () => setOrdering("temperature_mean"),
                },
                () =>
                    h(
                        "span",
                        { class: "whitespace-pre-line" },
                        "Température\nMoyenne",
                    ),
            ),
        cellCustom: ({ row }) =>
            `${row.getValue<number>("temperatureMean").toFixed(1)} °C`,
    }),
];
</script>

<template>
    <div class="flex flex-col gap-4">
        <div class="flex items-end justify-between gap-4">
            <DayPicker
                v-if="props.showFilters"
                v-model:start-date="dateStart"
                v-model:end-date="dateEnd"
                :min-date="dates.absoluteMinDataDate.value"
                :max-date="dates.yesterday.value"
            />
            <UButton
                label="Exporter CSV"
                icon="i-lucide-download"
                :ui="EXPORT_BTN_UI"
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
