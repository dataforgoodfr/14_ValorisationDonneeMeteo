<template>
    <UButton id="exportPngButton" color="neutral" @click="exportPngFnc">Export en png</UButton>
</template>

<script setup lang="ts">
import * as echarts from 'echarts';

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
    anchorElement.download = 'YYYYMMDD_HHMMSS_IndicateurThermiqueNational_XUnit_DT';

    document.body.appendChild(anchorElement);
    anchorElement.click();

    document.body.removeChild(anchorElement);
    window.URL.revokeObjectURL(href);
}

</script>
