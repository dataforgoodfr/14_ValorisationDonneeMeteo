<template>
    <div class="flex flex-col gap-3 md:w-52 md:shrink-0 py-2">
        <Card
            title="Écart à la normale moyen en France"
            :tooltip-text="`Écart à la normale moyen en France métropolitaine entre le ${formattedStart} et le ${formattedEnd}.`"
            :loading="pending"
        >
            <template #kpi>
                <p
                    class="font-semibold text-4xl mb-1"
                    :class="
                        (kpi?.deviation_from_normal ?? 0) >= 0
                            ? 'text-red-400'
                            : 'text-blue-400'
                    "
                >
                    <span v-if="kpi?.deviation_from_normal != null">
                        {{ kpi.deviation_from_normal >= 0 ? "+" : ""
                        }}{{ kpi.deviation_from_normal.toFixed(1) }} °C
                    </span>
                    <span v-else class="text-muted">—</span>
                </p>
            </template>
            <template #kpi-context-text> vs normales 1991–2020 </template>
        </Card>

        <Card
            title="Nombre de jours au-dessus des normales"
            :tooltip-text="`Nombre de jours, entre le ${formattedStart} et le ${formattedEnd}, pour lesquels l'écart à la normale en France métropolitaine est supérieur à 0.`"
            :loading="pending"
        >
            <template #kpi>
                <p class="font-semibold text-4xl mb-1 text-red-400">
                    <span v-if="kpi != null">{{
                        kpi.days_above_baseline
                    }}</span>
                    <span v-else class="text-muted">—</span>
                </p>
            </template>
            <template #kpi-context-text> vs normales 1991–2020 </template>
        </Card>

        <Card
            title="Nombre de jours en-dessous des normales"
            :tooltip-text="`Nombre de jours, entre le ${formattedStart} et le ${formattedEnd} pour lesquels l'écart à la normale en France métropolitaine est inférieur à 0.`"
            :loading="pending"
        >
            <template #kpi>
                <p class="font-semibold text-4xl mb-1 text-blue-400">
                    <span v-if="kpi != null">{{
                        kpi.days_below_baseline
                    }}</span>
                    <span v-else class="text-muted">—</span>
                </p>
            </template>
            <template #kpi-context-text> vs normales 1991–2020 </template>
        </Card>

        <HotColdRatioCard
            title="Jours chauds / froids"
            tooltip-text="Proportion de jours au-dessus des normales par rapport aux jours en-dessous des normales sur la période sélectionnée."
            :hot-value="kpi?.days_above_baseline ?? 0"
            :cold-value="kpi?.days_below_baseline ?? 0"
            hot-label="chauds"
            cold-label="froids"
            unit-label="jours"
        />
    </div>
</template>

<script setup lang="ts">
import Card from "~/components/home/Card.vue";
import HotColdRatioCard from "~/components/home/HotColdRatioCard.vue";
import { useDeviationStore, dateToStringYMD } from "#imports";
import type { NationalIndicatorKpiParams } from "~/types/api";

const store = useDeviationStore();
const { pickedDateStart, pickedDateEnd } = storeToRefs(store);

const fmt = (d: Date) => d.toLocaleDateString("fr-FR", { dateStyle: "short" });
const formattedStart = computed(() => fmt(pickedDateStart.value));
const formattedEnd = computed(() => fmt(pickedDateEnd.value));

const params = computed<NationalIndicatorKpiParams>(() => ({
    date_start: dateToStringYMD(pickedDateStart.value),
    date_end: dateToStringYMD(pickedDateEnd.value),
}));

const { data: kpi, pending } = useNationalIndicatorKpi(params);
</script>
