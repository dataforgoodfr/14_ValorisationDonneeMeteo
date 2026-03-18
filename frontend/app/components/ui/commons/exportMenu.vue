<script setup lang="ts">
import type { DropdownMenuItem } from "@nuxt/ui";
import { useItnStore } from "#imports";

const itnStore = useItnStore();
const { itnChartRef, granularity, pickedDateStart, pickedDateEnd, itnData } =
    storeToRefs(itnStore);

const exportMenuItems = ref<DropdownMenuItem[]>([
    {
        label: "Format PNG",
        icon: "i-lucide-file-image",
        onSelect(e: Event) {
            e.preventDefault();
            exportAsPng();
        },
    },
    {
        label: "Format CSV",
        icon: "i-lucide-file-spreadsheet",
        onSelect(e: Event) {
            e.preventDefault();
            exportAsCSV();
        },
    },
    {
        label: "Format HTML",
        icon: "i-lucide-file-code",
        onSelect(e: Event) {
            e.preventDefault();
            exportAsHTML();
        },
    },
]);

function exportAsPng() {
    if (!import.meta.client) return;
    const dataURL = itnChartRef.value.getDataURL({
        type: "png",
        pixelRatio: 2,
        backgroundColor: "#fff",
        excludeComponents: ["dataZoom"],
    });

    const a = document.createElement("a");
    a.href = dataURL;
    a.download = useFormatFileName(
        "itn",
        granularity.value,
        pickedDateStart.value,
        pickedDateEnd.value,
        "png",
    );
    a.click();
}

function exportAsCSV() {
    if (!import.meta.client) return;
    const source = itnData.value?.time_series;
    if (!source) return;
    const headers = [
        "Date",
        "Température observée en °C (moyenne/valeur selon slice_type)",
        "Température moyenne de référence 1991-2020 pour cette période en °C",
        "Écart-type supérieur en °C (moyenne + 1°C écart-type)",
        "Écart-type inférieur en °C (moyenne - 1°C écart-type)",
        "Température maximale observée sur la période 1991-2020 en °C ",
        "Température minimale observée sur la période 1991-2020 en °C ",
    ];
    const rows = source.map((row) => Object.values(row).join(",")).join("\n");

    const csv = `${headers}\n${rows}`;

    const a = document.createElement("a");
    a.href = `data:text/csv;charset=utf-8,${encodeURIComponent(csv)}`;
    a.download = useFormatFileName(
        "itn",
        granularity.value,
        pickedDateStart.value,
        pickedDateEnd.value,
        "csv",
    );
    a.click();
}

function exportAsHTML() {
    if (!import.meta.client) return;
    const options = itnChartRef.value.getOption();
    const scriptTag = "script";
    const html = `<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>ITN</title>
    <${scriptTag} src="https://cdn.jsdelivr.net/npm/echarts/dist/echarts.min.js"></${scriptTag}>
    <style>html { margin: 0; padding: 0; width: 100%; height: 100vh; }, body { display: flex; align-items: center; margin: 0; padding: 0; width: 100%; height: 100vh; } #chart { margin: 20px; width: auto; height: calc(100vh - 40px); }</style>
</head>
<body>
    <div id="chart"></div>
    <${scriptTag}>
        const chart = echarts.init(document.getElementById('chart'));
        chart.setOption(${JSON.stringify(options)});
        window.addEventListener('resize', () => chart.resize());
    </${scriptTag}>
</body>
</html>`;

    const a = document.createElement("a");
    a.href = `data:text/html;charset=utf-8,${encodeURIComponent(html)}`;
    a.download = useFormatFileName(
        "itn",
        granularity.value,
        pickedDateStart.value,
        pickedDateEnd.value,
        "html",
    );
    a.click();
}
</script>

<template>
    <UDropdownMenu
        :items="exportMenuItems"
        :ui="{}"
        :content="{
            align: 'start',
            side: 'bottom',
        }"
    >
        <UButton label="Exporter" icon="i-lucide-download" color="neutral" />
    </UDropdownMenu>
</template>
