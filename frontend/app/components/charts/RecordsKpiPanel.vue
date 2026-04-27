<template>
    <div class="flex flex-col gap-3 md:w-52 md:shrink-0 py-2">
        <Card
            :title="`Records de chaud (${kindLabel})`"
            :tooltip-text="`Nombre de records de chaleur ${kindLabel.toLowerCase()} en France entre le ${formattedStart} et le ${formattedEnd}.`"
        >
            <template #kpi>
                <p class="font-semibold text-4xl mb-1 text-red-400">
                    {{ hotCount }}
                </p>
            </template>
            <template #kpi-context-text>
                {{ formattedStart }} – {{ formattedEnd }}
            </template>
        </Card>

        <Card
            :title="`Records de froid (${kindLabel})`"
            :tooltip-text="`Nombre de records de froid ${kindLabel.toLowerCase()} en France entre le ${formattedStart} et le ${formattedEnd}.`"
        >
            <template #kpi>
                <p class="font-semibold text-4xl mb-1 text-blue-400">
                    {{ coldCount }}
                </p>
            </template>
            <template #kpi-context-text>
                {{ formattedStart }} – {{ formattedEnd }}
            </template>
        </Card>
    </div>
</template>

<script setup lang="ts">
import Card from "~/components/home/Card.vue";
import type { SelectBarAdapter } from "~/components/ui/commons/selectBar/types";
import type { TemperatureRecordsGraphResponse } from "~/types/api";

const props = defineProps<{
    adapter: SelectBarAdapter<TemperatureRecordsGraphResponse>;
}>();

const records = computed(() => props.adapter.data.value?.records ?? []);

const hotCount = computed(
    () => records.value.filter((r) => r.type_records === "hot").length,
);
const coldCount = computed(
    () => records.value.filter((r) => r.type_records === "cold").length,
);

const kindLabel = computed(() =>
    props.adapter.recordKind?.value === "historical"
        ? "Records battus"
        : "Records absolus",
);

const fmt = (d: Date) => d.toLocaleDateString("fr-FR", { dateStyle: "short" });
const formattedStart = computed(() => fmt(props.adapter.pickedDateStart.value));
const formattedEnd = computed(() => fmt(props.adapter.pickedDateEnd.value));
</script>
