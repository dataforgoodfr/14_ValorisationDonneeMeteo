<template>
    <div class="flex flex-col gap-3 w-52 shrink-0 py-2">
        <!-- <Card // à ajouter une fois le endpoint enrichi
            title="ITN moyen"
            tooltip-text="Moyenne de l'Indicateur Thermique National sur la période sélectionnée."
        >
            <template #kpi>
                <p
                    class="font-semibold text-4xl mb-1"
                    :class="
                        (hotKpi?.itn_mean ?? 0) >= 0
                            ? 'text-red-400'
                            : 'text-blue-400'
                    "
                >
                    <span v-if="hotKpi?.itn_mean != null">
                        {{ hotKpi.itn_mean >= 0 ? "+" : ""
                        }}{{ hotKpi.itn_mean.toFixed(1) }} °C
                    </span>
                    <span v-else class="text-muted">—</span>
                </p>
            </template>
            <template v-if="hotKpi?.deviation_from_normal != null" #variation>
                <span class="text-sm">
                    {{
                        hotKpi.deviation_from_normal >= 0 ? "+" : ""
                    }}{{ hotKpi.deviation_from_normal.toFixed(1) }}°C
                </span>
                <UIcon
                    v-if="hotKpi.deviation_from_normal < 0"
                    name="i-lucide-arrow-down-right"
                    class="text-blue-400"
                />
                <UIcon
                    v-if="hotKpi.deviation_from_normal > 0"
                    name="i-lucide-arrow-up-right"
                    class="text-red-400"
                />
                vs normale
            </template>
        </Card> -->

        <Card
            title="Jours de chaleur"
            tooltip-text="Nombre de jours avec excédent de chaleur sur la période sélectionnée."
        >
            <template #kpi>
                <p class="font-semibold text-4xl mb-1 text-red-400">
                    <span v-if="hotKpi != null">{{ hotKpi.count }}</span>
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
                    class="text-blue-400"
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
            title="Jours de froid"
            tooltip-text="Nombre de jours avec excédent de froid sur la période sélectionnée."
        >
            <template #kpi>
                <p class="font-semibold text-4xl mb-1 text-blue-400">
                    <span v-if="coldKpi != null">{{ coldKpi.count }}</span>
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
                    class="text-red-400"
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

const prevPeriod = computed(() => {
    const start = new Date(pickedDateStart.value);
    const end = new Date(pickedDateEnd.value);
    const durationMs = end.getTime() - start.getTime();
    const prevEnd = new Date(start.getTime() - 24 * 60 * 60 * 1000);
    const prevStart = new Date(
        start.getTime() - durationMs - 24 * 60 * 60 * 1000,
    );
    return {
        date_start: dateToStringYMD(prevStart),
        date_end: dateToStringYMD(prevEnd),
    };
});

const hotParams = computed<NationalIndicatorKpiParams>(() => ({
    date_start: dateToStringYMD(new Date(pickedDateStart.value)),
    date_end: dateToStringYMD(new Date(pickedDateEnd.value)),
    type: "hot",
}));

const coldParams = computed<NationalIndicatorKpiParams>(() => ({
    date_start: dateToStringYMD(new Date(pickedDateStart.value)),
    date_end: dateToStringYMD(new Date(pickedDateEnd.value)),
    type: "cold",
}));

const prevHotParams = computed<NationalIndicatorKpiParams>(() => ({
    ...prevPeriod.value,
    type: "hot",
}));
const prevColdParams = computed<NationalIndicatorKpiParams>(() => ({
    ...prevPeriod.value,
    type: "cold",
}));

const { data: hotKpi } = useNationalIndicatorKpi(hotParams);
const { data: coldKpi } = useNationalIndicatorKpi(coldParams);
const { data: prevHotKpi } = useNationalIndicatorKpi(prevHotParams);
const { data: prevColdKpi } = useNationalIndicatorKpi(prevColdParams);

const hotDiff = computed(() => {
    if (hotKpi.value == null || prevHotKpi.value == null) return null;
    return hotKpi.value.count - prevHotKpi.value.count;
});

const coldDiff = computed(() => {
    if (coldKpi.value == null || prevColdKpi.value == null) return null;
    return coldKpi.value.count - prevColdKpi.value.count;
});
</script>
