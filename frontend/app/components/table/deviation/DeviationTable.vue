<script setup lang="ts">
import { h } from "vue";
import { UBadge, UButton } from "#components";
import {
    CENTERED_TD,
    makeSortableColFactory,
    REGION_META,
    STATION_META,
    TABLE_HEADER_BTN_MULTILINE_CLASS,
    TEMPERATURE_BADGE_SIZE,
    temperatureBadgeClass,
    truncatedCell,
} from "~/constants/tableUtils";
import { storeToRefs } from "pinia";
import { useDeviationTableStore } from "~/stores/deviationTableStore";
import DayPicker from "~/components/ui/commons/selectBar/dayPicker.vue";
import { useCustomDate } from "~/composables/useCustomDate";
import type { TemperatureDeviationResponse } from "~/types/api";

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
    error,
    dateStart,
    dateEnd,
    ordering,
    pending,
    hasActiveFilters,
} = storeToRefs(store);
const { resetFilters } = store;

const { setOrdering } = store;

interface TableRow {
    station_name: string;
    department: string;
    region: string;
    deviation: number;
    temperatureMean: number;
    classeRecente: number;
    anneeDeCreation: number;
}

const tableData = computed<TableRow[]>(() => {
    const data: TemperatureDeviationResponse | undefined = deviationData.value;
    return (data?.stations ?? []).map((s) => ({
        station_name: s.station_name,
        department: s.department,
        region: s.region,
        deviation: s.deviation,
        temperatureMean: s.temperature_mean,
        classeRecente: s.classe_recente,
        anneeDeCreation: new Date(s.date_de_creation).getFullYear(),
    }));
});

const deviationBadgeColor = (deviation: number) =>
    deviation >= 0 ? "error" : "info";

const sortableCol = makeSortableColFactory<TableRow>(ordering, setOrdering);

const columns = [
    sortableCol("station_name", "Station", {
        meta: STATION_META,
        cellCustom: ({ row }) => truncatedCell(row.getValue("station_name")),
    }),
    sortableCol("department", "Département", {
        meta: CENTERED_TD,
    }),
    sortableCol("region", "Région", {
        meta: REGION_META,
        cellCustom: ({ row }) => truncatedCell(row.getValue("region")),
    }),
    sortableCol("deviation", "Écart à la normale", {
        meta: CENTERED_TD,
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
        cellCustom: ({ row }) =>
            `${row.getValue<number>("temperatureMean").toFixed(1)} °C`,
    }),
    sortableCol("classeRecente", "Classe", {
        sortKey: "classe_recente",
        meta: CENTERED_TD,
    }),
    sortableCol("anneeDeCreation", "Année de création", {
        sortKey: "date_de_creation",
        meta: CENTERED_TD,
        headerCustom: () =>
            h(
                UButton,
                {
                    variant: "ghost",
                    trailingIcon: ordering.value.includes("date_de_creation")
                        ? ordering.value.startsWith("-")
                            ? "i-lucide-arrow-down"
                            : "i-lucide-arrow-up"
                        : "i-lucide-arrow-up-down",
                    color: "neutral",
                    class: TABLE_HEADER_BTN_MULTILINE_CLASS,
                    onClick: () => setOrdering("date_de_creation"),
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
        <DayPicker
            v-if="props.showFilters"
            v-model:start-date="dateStart"
            v-model:end-date="dateEnd"
            :min-date="dates.absoluteMinDataDate.value"
            :max-date="dates.yesterday.value"
        />

        <div v-if="error" class="px-4 py-3 bg-error/10 text-error rounded">
            Erreur de chargement : {{ error }}
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
                <tr v-for="i in 10" :key="i">
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
                <div class="flex flex-col items-center gap-3 py-8 text-muted">
                    <span>Aucune donnée affichée.</span>
                    <UButton
                        v-if="hasActiveFilters"
                        label="Réinitialiser les filtres"
                        icon="i-lucide-filter-x"
                        :ui="EXPORT_BTN_UI"
                        @click="resetFilters"
                    />
                </div>
            </template>
        </UTable>

        <div class="flex justify-center border-t border-accented pt-4">
            <UPagination
                v-model:page="page"
                :total="deviationData?.pagination.total_count ?? 0"
                :items-per-page="pageSize"
            />
        </div>
    </div>
</template>
