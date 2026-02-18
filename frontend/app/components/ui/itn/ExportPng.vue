<template>
    <UButton id="exportPngButton" color="neutral" @click="exportPngFnc">Export en png</UButton>
</template>

<script setup lang="ts">
import * as echarts from 'echarts';

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

async function exportPngFnc(){
    const img = new Image();
    const chart = echarts.getInstanceByDom(document.getElementById('itnCombinedChart'));
    img.src = chart.getDataURL({
        type:"png",
        pixelRatio: 2,
        backgroundColor: '#fff'
    });

    const response = await fetch(img.src);

    const blobImage = await response.blob();

    const href = URL.createObjectURL(blobImage);

    const anchorElement = document.createElement('a');
    anchorElement.href = href;
    // ATTENTION : l'intervalle de temps est codé en dur !
    anchorElement.download = formatFileName('mois', '20251001_to_20251231');

    document.body.appendChild(anchorElement);
    anchorElement.click();

    document.body.removeChild(anchorElement);
    window.URL.revokeObjectURL(href);
}

</script>
