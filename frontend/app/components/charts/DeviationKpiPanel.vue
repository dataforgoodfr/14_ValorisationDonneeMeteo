<template>
    <div
        class="flex flex-col gap-3 py-2"
        :class="compact ? 'w-full' : 'md:w-52 md:shrink-0'"
    >
        <Card
            title="Écart à la normale moyen en France"
            :tooltip-text="`Écart à la normale moyen en France métropolitaine entre le ${formattedStart} et le ${formattedEnd}.`"
            :loading="pending"
        >
            <template #kpi>
                <p
                    class="font-semibold text-4xl mb-1"
                    :class="deviationColorClass"
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
            v-if="!compact"
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
            v-if="!compact"
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
            :pending="pending"
        />
    </div>
</template>

<script setup lang="ts">
import Card from "~/components/home/Card.vue";
import HotColdRatioCard from "~/components/home/HotColdRatioCard.vue";
import { useDeviationStore, dateToStringYMD } from "#imports";
import type { NationalIndicatorKpiParams } from "~/types/api";

interface Props {
    dateStart?: string;
    dateEnd?: string;
    compact?: boolean;
}
const props = defineProps<Props>();

const store = useDeviationStore();
const { effectiveDateStart, effectiveDateEnd } = storeToRefs(store);

const fmt = (d: Date) => d.toLocaleDateString("fr-FR", { dateStyle: "short" });
const formattedStart = computed(() =>
    props.dateStart
        ? fmt(new Date(props.dateStart))
        : fmt(effectiveDateStart.value),
);
const formattedEnd = computed(() =>
    props.dateEnd ? fmt(new Date(props.dateEnd)) : fmt(effectiveDateEnd.value),
);

const params = computed<NationalIndicatorKpiParams>(() => ({
    date_start: props.dateStart ?? dateToStringYMD(effectiveDateStart.value),
    date_end: props.dateEnd ?? dateToStringYMD(effectiveDateEnd.value),
}));

const { data: kpi, pending } = useNationalIndicatorKpi(params);

const deviationColorClass = computed(() => {
    const deviation = kpi.value?.deviation_from_normal;
    if (deviation == null) return "text-green-400";
    if (deviation > 0) return "text-red-400";
    if (deviation < 0) return "text-blue-400";
    return "text-green-400";
});
</script>
