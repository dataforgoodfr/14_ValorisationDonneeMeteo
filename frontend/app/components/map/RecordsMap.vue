<template>
    <div class="flex flex-col gap-0 lg:w-155 w-full shrink-0">
        <StationMap
            class="-mt-20"
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
const store = useRecordsTableStore();

const mappableStations = computed<MappableStation[]>(() =>
    store.filteredRecords.map((s) => ({
        lat: s.lat,
        lon: s.lon,
        station_name: s.station_name,
        value: s.record_value,
        record_date: s.record_date,
        department: s.department,
    })),
);

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
