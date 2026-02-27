<template>
    <UButton id="exportHtmlButton" color="neutral" @click="exportHtmlFnc"
        >Export en HTML</UButton
    >
</template>

<script setup lang="ts">
import * as echarts from "echarts";

async function exportHtmlFnc() {
    const img = new Image();
    const itnCombinedChartElement = document.getElementById("itnCombinedChart");
    if (itnCombinedChartElement != null) {
        const chart = echarts.getInstanceByDom(itnCombinedChartElement);

        if (chart) {
            img.src = chart.getDataURL({
                type: "png",
                pixelRatio: 2,
                backgroundColor: "#fff",
            });

            const response = await fetch(img.src);

            const blobImage = await response.blob();

            const fileURL = URL.createObjectURL(blobImage);
            window.open(fileURL, "_blank");
            URL.revokeObjectURL(fileURL);
        } else {
            throw showError(
                "La variable 'chart' est 'undefined'. Veuillez contacter votre administrateur.",
            );
        }
    } else {
        throw showError(
            "La balise html 'itnCombinedChart' n'existe pas. Veuillez contacter votre administrateur.",
        );
    }
}
</script>
