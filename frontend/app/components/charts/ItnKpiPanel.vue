<template>
    <div class="flex flex-col gap-3 md:w-52 md:shrink-0 py-2">
        <Card
            title="ITN moyen"
            tooltip-text="Moyenne de l'Indicateur Thermique National sur la période sélectionnée."
        >
            <template #kpi>
                <p class="font-semibold text-4xl mb-1 text-red-400">
                    <span v-if="kpi != null"
                        >{{ kpi.itn_mean?.toFixed(1) }} °C</span
                    >
                    <span v-else class="text-muted">—</span>
                </p>
            </template>
            <template v-if="kpi?.deviation_from_normal != null" #variation>
                <span class="text-sm">
                    {{ kpi.deviation_from_normal >= 0 ? "+" : ""
                    }}{{ kpi.deviation_from_normal.toFixed(1) }} °C
                </span>
                <UIcon
                    v-if="kpi.deviation_from_normal < 0"
                    name="i-lucide-arrow-down-right"
                    class="text-blue-400"
                />
                <UIcon
                    v-if="kpi.deviation_from_normal > 0"
                    name="i-lucide-arrow-up-right"
                    class="text-red-400"
                />
                vs période des normales
            </template>
        </Card>

        <Card
            title="Nombre de jours anormalement chauds"
            tooltip-text="Nombre de jours, sur la période sélectionnée, pour lesquels la température en France est supérieure aux normales."
        >
            <template #kpi>
                <p class="font-semibold text-4xl mb-1 text-red-400">
                    <span v-if="kpi != null">{{ kpi.hot_peak_count }}</span>
                    <span v-else class="text-muted">—</span>
                </p>
            </template>
            <template v-if="hotDiff != null" #variation>
                <span class="text-sm">
                    {{ hotDiff >= 0 ? "+" : "" }}{{ hotDiff }}
                </span>
                <UIcon
                    v-if="hotDiff < 0"
                    name="i-lucide-arrow-down-right"
                    class="text-red-400"
                />
                <UIcon
                    v-if="hotDiff > 0"
                    name="i-lucide-arrow-up-right"
                    class="text-red-400"
                />
                vs période précédente
            </template>
        </Card>

        <Card
            title="Nombre de jours anormalement froids"
            tooltip-text="Nombre de jours, sur la période sélectionnée, pour lesquels la température en France est inférieure aux normales."
        >
            <template #kpi>
                <p class="font-semibold text-4xl mb-1 text-blue-400">
                    <span v-if="kpi != null">{{ kpi.cold_peak_count }}</span>
                    <span v-else class="text-muted">—</span>
                </p>
            </template>
            <template v-if="coldDiff != null" #variation>
                <span class="text-sm">
                    {{ coldDiff >= 0 ? "+" : "" }}{{ coldDiff }}
                </span>
                <UIcon
                    v-if="coldDiff < 0"
                    name="i-lucide-arrow-down-right"
                    class="text-blue-400"
                />
                <UIcon
                    v-if="coldDiff > 0"
                    name="i-lucide-arrow-up-right"
                    class="text-blue-400"
                />
                vs période précédente
            </template>
        </Card>
    </div>
</template>

<script setup lang="ts">
import Card from "~/components/home/Card.vue";
import { useItnStore } from "~/stores/itnStore";
import { dateToStringYMD } from "#imports";
import type { NationalIndicatorKpiParams } from "~/types/api";

const store = useItnStore();
const { pickedDateStart, pickedDateEnd } = storeToRefs(store);

const params = computed<NationalIndicatorKpiParams>(() => ({
    date_start: dateToStringYMD(pickedDateStart.value),
    date_end: dateToStringYMD(pickedDateEnd.value),
}));

const { data: kpi } = useNationalIndicatorKpi(params);

const hotDiff = computed(() => {
    if (kpi.value == null) return null;
    return kpi.value.hot_peak_count - kpi.value.previous.hot_peak_count;
});

const coldDiff = computed(() => {
    if (kpi.value == null) return null;
    return kpi.value.cold_peak_count - kpi.value.previous.cold_peak_count;
});
</script>
