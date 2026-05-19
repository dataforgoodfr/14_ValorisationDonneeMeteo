<template>
    <div class="flex flex-col gap-3 md:w-52 md:shrink-0 py-2">
        <Card
            title="ITN moyen"
            :tooltip-text="`Moyenne de l'Indicateur Thermique National du ${formattedStart} au ${formattedEnd}.`"
            :loading="pending"
        >
            <template #kpi>
                <p class="font-semibold text-4xl mb-1" :class="itnColorClass">
                    <span v-if="kpi != null"
                        >{{ kpi.itn_mean?.toFixed(1) }} °C</span
                    >

                    <span v-else class="text-muted">—</span>
                </p>
            </template>
            <template #variation>
                <template v-if="kpi?.deviation_from_normal != null">
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
                    vs normales 1991-2020
                </template>

                <span v-else class="text-muted">—</span>
            </template>
        </Card>

        <Card
            title="Nombre de jours excessivement chauds"
            :tooltip-text="`Nombre de jours, entre le ${formattedStart} et le ${formattedEnd}, pour lesquels la valeur de l'ITN est au-delà de l'écart-type des normales 1991-2020.`"
        >
            <template #kpi>
                <p class="font-semibold text-4xl mb-1 text-red-400">
                    <UIcon
                        v-if="pending"
                        name="i-lucide-loader-circle"
                        class="animate-spin text-5xl text-muted"
                    />

                    <span v-else-if="kpi != null">{{
                        kpi.hot_peak_count
                    }}</span>

                    <span v-else class="text-muted">—</span>
                </p>
            </template>
            <template #variation>
                <USkeleton v-if="pending" class="h-2 w-full" />

                <template v-else-if="hotDiff != null">
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

                <span v-else class="text-muted">—</span>
            </template>
        </Card>

        <Card
            title="Nombre de jours excessivement froids"
            :tooltip-text="`Nombre de jours du ${formattedStart} au ${formattedEnd} pour lesquels la valeur de l'ITN est en-deçà de l'écart-type de la période des normales.`"
        >
            <template #kpi>
                <p class="font-semibold text-4xl mb-1 text-blue-400">
                    <UIcon
                        v-if="pending"
                        name="i-lucide-loader-circle"
                        class="animate-spin text-5xl text-muted"
                    />
                    <span v-else-if="kpi != null">{{
                        kpi.cold_peak_count
                    }}</span>
                    <span v-else class="text-muted">—</span>
                </p>
            </template>
            <template #variation>
                <USkeleton v-if="pending" class="h-2 w-full" />

                <template v-else-if="coldDiff != null">
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

                <span v-else class="text-muted">—</span>
            </template>
        </Card>

        <HotColdRatioCard
            title="Excès de chaleur / froid"
            :tooltip-text="`Proportion de jours excessivement chauds par rapport aux jours excessivement froids du ${formattedStart} au ${formattedEnd}.`"
            :hot-value="kpi?.hot_peak_count ?? 0"
            :cold-value="kpi?.cold_peak_count ?? 0"
            hot-label="chaleur"
            cold-label="froid"
            unit-label="jours avec excès de"
            :pending="pending"
        />
    </div>
</template>

<script setup lang="ts">
import Card from "~/components/home/Card.vue";
import HotColdRatioCard from "~/components/home/HotColdRatioCard.vue";
import { useItnStore } from "~/stores/itnStore";
import { dateToStringYMD } from "#imports";
import type { NationalIndicatorKpiParams } from "~/types/api";

const store = useItnStore();
const { effectiveDateStart, effectiveDateEnd } = storeToRefs(store);

const fmt = (d: Date) => d.toLocaleDateString("fr-FR", { dateStyle: "short" });
const formattedStart = computed(() => fmt(effectiveDateStart.value));
const formattedEnd = computed(() => fmt(effectiveDateEnd.value));

const params = computed<NationalIndicatorKpiParams>(() => ({
    date_start: dateToStringYMD(effectiveDateStart.value),
    date_end: dateToStringYMD(effectiveDateEnd.value),
}));

const { data: kpi, pending } = useNationalIndicatorKpi(params);

const itnColorClass = computed(() => {
    const deviation = kpi.value?.deviation_from_normal;
    if (deviation == null) return "text-green-400";
    if (deviation > 0) return "text-red-400";
    if (deviation < 0) return "text-blue-400";
    return "text-green-400";
});

const hotDiff = computed(() => {
    if (kpi.value == null) return null;
    return kpi.value.hot_peak_count - kpi.value.previous.hot_peak_count;
});

const coldDiff = computed(() => {
    if (kpi.value == null) return null;
    return kpi.value.cold_peak_count - kpi.value.previous.cold_peak_count;
});
</script>
