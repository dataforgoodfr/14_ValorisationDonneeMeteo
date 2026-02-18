<template>
    <UButton id="exportPngButton" color="neutral" @click="exportPngFnc">Export en png</UButton>
</template>

<script setup lang="ts">
import * as echarts from 'echarts';

function exportPngFnc(){
    console.log("export PNG")
    const img = new Image();
    console.log(document.getElementById('itn_combined_chart'));
    const chart = echarts.getInstanceByDom(document.getElementById('itnCombinedChart'));
    img.src = chart.getDataURL({
        type:"png",
        pixelRatio: 2,
        backgroundColor: '#fff'
    });
    console.log(img.src)

}

</script>
