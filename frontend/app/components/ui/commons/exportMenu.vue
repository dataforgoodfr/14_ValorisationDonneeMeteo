<script setup lang="ts">
import type { DropdownMenuItem } from "@nuxt/ui";
import { useItnStore } from "#imports";

const itnStore = useItnStore();
const {
    itnChartRef,
    granularity,
    picked_date_start,
    picked_date_end,
    itnData,
} = storeToRefs(itnStore);

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
        picked_date_start.value,
        picked_date_end.value,
        "png",
    );
    a.click();
}

function exportAsCSV() {
    const source = itnData.value?.time_series;
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
    const blob = new Blob([csv], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);

    const anchorElement = document.createElement("a");
    anchorElement.href = url;
    anchorElement.download = useFormatFileName(
        "itn",
        granularity.value,
        picked_date_start.value,
        picked_date_end.value,
        "csv",
    );
    anchorElement.click();

    window.URL.revokeObjectURL(url);
}
async function exportAsHTML() {
    if (!import.meta.client) return;
    const dataURL = itnChartRef.value.getDataURL({
        type: "png",
        pixelRatio: 2,
        backgroundColor: "#fff",
        excludeComponents: ["dataZoom"],
    });
    const html = `
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8"><title>Mon graphique</title></head>
        <body>
        <img src="${dataURL}" alt="Graphique">
        </body>
        </html>
        `;

    const blob = new Blob([html], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'graphique.html';
    a.click();
    URL.revokeObjectURL(url);
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
