<template>
    <div class="flex flex-col gap-2 w-[700px] flex-shrink-0">
        <Card
            class="w-fit mx-auto"
            :with-border="false"
            :title="`Record ${store.typeRecords === 'hot' ? 'chaud' : 'froid'} le plus extrême`"
            tooltip-text="Station avec le record absolu sur la période sélectionnée"
        >
            <template #kpi>
                <span
                    v-if="extremeStation"
                    class="text-lg font-semibold"
                    :class="
                        store.typeRecords === 'hot'
                            ? 'text-red-400'
                            : 'text-blue-400'
                    "
                >
                    {{ extremeStation.record_value >= 0 ? "+" : ""
                    }}{{ extremeStation.record_value.toFixed(1) }} °C
                </span>
                <span v-else class="text-lg font-semibold text-muted">—</span>
            </template>
            <template #kpi-context-text>
                <template v-if="extremeStation">
                    {{ extremeStation.station_name }} ·
                    {{ extremeStation.department }} ·
                    {{ formatDate(extremeStation.record_date) }}
                </template>
                <template v-else>—</template>
            </template>
        </Card>
        <StationMap
            :stations="mappableStations"
            :color-config="RECORDS_MAP_COLORS"
            :tooltip-formatter="tooltipFormatter"
            legend-label="Record absolu (°C)"
        />
    </div>
</template>

<script setup lang="ts">
import { useRecordsTableStore } from "~/stores/recordsTableStore";
import type { MappableStation } from "~/types/api";
import { RECORDS_MAP_COLORS } from "~/constants/colors";
import { formatRecordsMapTooltip } from "~/components/map/tooltipFormatters/recordsMapTooltipFormatter";
import StationMap from "~/components/map/StationMap.vue";
import Card from "~/components/home/Card.vue";
const store = useRecordsTableStore();

const extremeStation = computed(() => {
    const records = store.absoluteRecords;
    if (!records.length) return null;
    if (store.typeRecords === "hot") {
        return records.reduce((best, r) =>
            r.record_value > best.record_value ? r : best,
        );
    }
    return records.reduce((best, r) =>
        r.record_value < best.record_value ? r : best,
    );
});

const mappableStations = computed<MappableStation[]>(() =>
    store.absoluteRecords.map((s) => ({
        lat: s.lat,
        lon: s.lon,
        station_name: s.station_name,
        value: s.record_value,
        record_date: s.record_date,
        department: s.department,
    })),
);

function formatDate(dateStr: string): string {
    return new Date(dateStr).toLocaleDateString("fr-FR");
}

const tooltipFormatter = (properties: {
    station_name: string;
    value: number;
    record_date: string | null;
    department: string | null;
}) =>
    formatRecordsMapTooltip(
        properties.station_name,
        properties.value,
        properties.record_date,
    );
</script>
