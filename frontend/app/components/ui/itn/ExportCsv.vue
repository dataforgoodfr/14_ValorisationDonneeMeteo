<template>
    <UButton id="exportCsvButton" color="neutral" @click="exportCsvFnc">Export en CSV</UButton>
</template>


<script setup lang="ts">
import { GetChartData, TimeAxisType } from "~~/public/ChartDataProvider";
const source = GetChartData(TimeAxisType.Day);

function formatDateManually(date) {
  // Helper function to pad numbers with a leading zero
  const pad = (num) => num.toString().padStart(2, '0');

  const year = date.getFullYear();
  const month = pad(date.getMonth() + 1); // getMonth() is zero-based (0-11)
  const day = pad(date.getDate());

  const hours = pad(date.getHours());
  const minutes = pad(date.getMinutes());
  const seconds = pad(date.getSeconds());

  return `${year}${month}${day}_${hours}${minutes}${seconds}`;
};

function formatFileName(xUnit: string, dt: string){
    const now = new Date(Date.now());
    // Question : date UTC ou locale ??
    return `${formatDateManually(now)}_IndicateurThermiqueNational_${xUnit}_${dt}`
};


async function exportCsvFnc(){

    console.log(`data = ${JSON.stringify(source)}`);
    const headers = ['Date', 'ITN - Température (°C)', 'Delta - Température (°C)', 'StdDev - Température (°C)', 'Min - Température (°C)', 'Max - Température (°C)'];
    const rows = source.map(row =>
        Object.values(row).join(',')
    ).join('\n');

    const csv = `${headers}\n${rows}`;
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);

    const anchorElement = document.createElement('a');
    anchorElement.href = url;
    // ATTENTION : l'intervalle de temps pour le nom du fichier est codé en dur !
    anchorElement.download = formatFileName('mois', '20251001_to_20251231');
    anchorElement.click();

    window.URL.revokeObjectURL(url);
}

</script>
