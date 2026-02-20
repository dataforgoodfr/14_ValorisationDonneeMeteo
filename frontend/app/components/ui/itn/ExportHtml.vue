<template>
    <UButton id="exportHtmlButton" color="neutral" @click="exportHtmlFnc">Export en HTML</UButton>
</template>


<script setup lang="ts">
import * as echarts from 'echarts';

async function exportHtmlFnc(){
    const img = new Image();
    const chart = echarts.getInstanceByDom(document.getElementById('itnCombinedChart'));
    img.src = chart.getDataURL({
        type:"png",
        pixelRatio: 2,
        backgroundColor: '#fff'
    });

    const response = await fetch(img.src);

    const blobImage = await response.blob();

    const fileURL = URL.createObjectURL(blobImage);
    window.open(fileURL, "_blank");
    URL.revokeObjectURL(fileURL);
}

</script>
