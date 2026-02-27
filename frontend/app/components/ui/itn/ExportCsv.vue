<template>
    <UButton id="exportCsvButton" color="neutral" @click="exportCsvFnc"
        >Export en CSV</UButton
    >
</template>

<script setup lang="ts">
import { GetChartData, TimeAxisType } from "~~/public/ChartDataProvider";
import { formatFileName } from "~~/public/utils";

const source = GetChartData(TimeAxisType.Day);

async function exportCsvFnc() {
    console.log(`data = ${JSON.stringify(source)}`);
    const headers = [
        "Date",
        "ITN - Température (°C)",
        "Delta - Température (°C)",
        "StdDev - Température (°C)",
        "Min - Température (°C)",
        "Max - Température (°C)",
    ];
    const rows = source.map((row) => Object.values(row).join(",")).join("\n");

    const csv = `${headers}\n${rows}`;
    const blob = new Blob([csv], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);

    const anchorElement = document.createElement("a");
    anchorElement.href = url;
    // ATTENTION : l'intervalle de temps pour le nom du fichier est codé en dur !
    anchorElement.download = formatFileName("mois", "20251001_to_20251231");
    anchorElement.click();

    window.URL.revokeObjectURL(url);
}
</script>
