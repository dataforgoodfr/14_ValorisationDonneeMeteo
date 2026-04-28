<script setup lang="ts">
import type { DropdownMenuItem } from "@nuxt/ui";
import type { SelectBarAdapter } from "./selectBar/types";
import { useMapColors } from "~/constants/colors";

const mapColors = useMapColors();

const adapter = inject<SelectBarAdapter>("selectBarAdapter")!;
const { exportConfig, chartRef, granularity, pickedDateStart, pickedDateEnd } =
    adapter;

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
        label: "Format PNG sans fond",
        icon: "i-lucide-file-image",
        onSelect(e: Event) {
            e.preventDefault();
            exportAsPngWithoutBackground();
        },
    },
    {
        label: "Format PNG fond blanc",
        icon: "i-lucide-file-image",
        onSelect(e: Event) {
            e.preventDefault();
            exportAsPngWhiteBackground();
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
    if (!chartRef?.value) return;
    const dataURL = chartRef.value.getDataURL({
        type: "png",
        pixelRatio: 2,
        backgroundColor: mapColors.value.background,
        excludeComponents: ["dataZoom"],
    });

    const a = document.createElement("a");
    a.href = dataURL;
    a.download = useFormatFileName(
        exportConfig.chartName,
        granularity.value,
        "png",
        pickedDateStart.value,
        pickedDateEnd.value,
    );
    a.click();
}

function exportAsPngWithoutBackground() {
    if (!import.meta.client) return;
    if (!chartRef?.value) return;
    const dataURL = chartRef.value.getDataURL({
        type: "png",
        pixelRatio: 2,
        backgroundColor: "transparent",
        excludeComponents: ["dataZoom"],
    });

    const a = document.createElement("a");
    a.href = dataURL;
    a.download = useFormatFileName(
        exportConfig.chartName,
        granularity.value,
        "png",
        pickedDateStart.value,
        pickedDateEnd.value,
    );
    a.click();
}

function exportAsPngWhiteBackground() {
    if (!import.meta.client) return;
    if (!chartRef?.value) return;
    const dataURL = chartRef.value.getDataURL({
        type: "png",
        pixelRatio: 2,
        backgroundColor: "#ffffff",
        excludeComponents: ["dataZoom"],
    });

    const a = document.createElement("a");
    a.href = dataURL;
    a.download = useFormatFileName(
        exportConfig.chartName,
        granularity.value,
        "png",
        pickedDateStart.value,
        pickedDateEnd.value,
    );
    a.click();
}

function exportAsCSV() {
    if (!import.meta.client) return;
    const source = exportConfig.getCsvRows();
    if (!source) return;
    const headers = exportConfig.csvHeaders;
    const rows = source.map((row) => Object.values(row).join(",")).join("\n");

    const csv = `${headers}\n${rows}`;

    const a = document.createElement("a");
    a.href = `data:text/csv;charset=utf-8,${encodeURIComponent(csv)}`;
    a.download = useFormatFileName(
        exportConfig.chartName,
        granularity.value,
        "csv",
        pickedDateStart.value,
        pickedDateEnd.value,
    );
    a.click();
}

function exportAsHTML() {
    if (!import.meta.client) return;
    if (!chartRef?.value) return;
    const options = chartRef.value.getOption();
    const scriptTag = "script";
    const html = `<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>${exportConfig.chartName.toUpperCase()}</title>
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
        "html",
        pickedDateStart.value,
        pickedDateEnd.value,
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
        <UButton
            label="Exporter"
            icon="i-lucide-download"
            :ui="{ base: 'bg-slate-450 ring-1 ring-blue-350 text-white' }"
        />
    </UDropdownMenu>
</template>
