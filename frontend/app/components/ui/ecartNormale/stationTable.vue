<script setup lang="ts">
import type { TableColumn } from "@nuxt/ui";
import { h } from "vue";
import type { TemperatureRecord } from "~/types/api";
import { UBadge, UInput } from "#components";
import { storeToRefs } from "pinia";
import { useRecordsStore } from "~/stores/recordsStore";

const RECORD_TYPE_TO_BADGE_COLOR = {
    Chaud: "error" as const,
    Froid: "info" as const,
};

const store = useRecordsStore();
const {
    recordType,
    startDate,
    endDate,
    page,
    pageSize,
    columnFilters,
    recordsData,
    pending,
    error,
} = storeToRefs(store);

const temperatureBadgeColor = computed(
    () => RECORD_TYPE_TO_BADGE_COLOR[recordType.value],
);

// Column filter helpers — read/write store's columnFilters
function getFilter(id: string): string {
    return (
        (columnFilters.value.find((f) => f.id === id)?.value as string) ?? ""
    );
}

function setFilter(id: string, value: string) {
    columnFilters.value = [
        ...columnFilters.value.filter((f) => f.id !== id),
        ...(value ? [{ id, value }] : []),
    ];
}

function filterInput(id: string) {
    return h(UInput, {
        modelValue: getFilter(id),
        "onUpdate:modelValue": (v: string) => setFilter(id, v),
        placeholder: "Filtrer...",
        size: "xs",
    });
}

// Column definitions — only depends on recordType, not on columnFilters (avoids focus loss)
const columns = computed<TableColumn<TemperatureRecord>[]>(() => [
    {
        accessorKey: "name",
        header: () =>
            h("div", { class: "flex flex-col gap-1" }, [
                h("span", "Station"),
                filterInput("name"),
            ]),
    },
    {
        accessorKey: "departement",
        header: () =>
            h("div", { class: "flex flex-col gap-1" }, [
                h("span", "Département"),
                filterInput("departement"),
            ]),
    },
    {
        accessorKey: "record",
        header: () =>
            h("div", { class: "flex flex-col gap-1" }, [
                h("span", "Record"),
                filterInput("record"),
            ]),
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
    {
        accessorKey: "record_date",
        header: () =>
            h("div", { class: "flex flex-col gap-1" }, [
                h("span", "Date du record"),
                filterInput("record_date"),
            ]),
    },
]);
</script>

<template>
    <div class="flex flex-col gap-4">
        <!-- Filters -->
        <div class="flex justify-between px-4 py-3.5 border-b border-accented">
            <div class="flex gap-4">
                <UFormField label="Date de début">
                    <UInput v-model="startDate" type="date" />
                </UFormField>
                <UFormField label="Date de fin">
                    <UInput v-model="endDate" type="date" />
                </UFormField>
            </div>

            <UFieldGroup>
                <UButton
                    class="cursor-pointer"
                    color="neutral"
                    :variant="recordType == 'Chaud' ? 'subtle' : 'outline'"
                    label="Chaud"
                    @click="recordType = 'Chaud'"
                />
                <UButton
                    class="cursor-pointer"
                    color="neutral"
                    :variant="recordType == 'Froid' ? 'subtle' : 'outline'"
                    label="Froid"
                    @click="recordType = 'Froid'"
                />
            </UFieldGroup>
        </div>

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
