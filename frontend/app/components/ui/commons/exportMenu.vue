<script setup lang="ts">
import type { DropdownMenuItem } from "@nuxt/ui";
import type { ShallowRef } from "vue";
import type {
    NationalIndicatorResponse,
    DeviationResponse
} from "~/types/api";

const props = defineProps({
  chart: {
    type: String,
    required: true
  }
})
const chartName = props.chart;

const itnStore = useItnStore();
const deviationStore = useDeviationStore();
let store;

let chartRef: ShallowRef<unknown, unknown>;
let granularity: globalThis.Ref<"month" | "year" | "day", "month" | "year" | "day">;
let picked_date_start: Ref<Date, Date>;
let picked_date_end: Ref<Date, Date>;
let data: Ref<NationalIndicatorResponse | undefined> | Ref<DeviationResponse | undefined>;
let headers: string[];

if (chartName == 'itn') {
    store = itnStore;
    headers = [
        "Date",
        "Température observée en °C (moyenne/valeur selon slice_type)",
        "Température moyenne de référence 1991-2020 pour cette période en °C",
        "Écart-type supérieur en °C (moyenne + 1°C écart-type)",
        "Écart-type inférieur en °C (moyenne - 1°C écart-type)",
        "Température maximale observée sur la période 1991-2020 en °C ",
        "Température minimale observée sur la période 1991-2020 en °C ",
    ];

} else { // chartName == 'ecart_normale'
    store = deviationStore;
    headers = ['date', 'écart à la normale'];
}

({
    chartRef,
    granularity,
    picked_date_start,
    picked_date_end,
    data,
} = storeToRefs(store));

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
    const dataURL = chartRef.value.getDataURL({
        type: "png",
        pixelRatio: 2,
        backgroundColor: "#fff",
        excludeComponents: ["dataZoom"],
    });

    const a = document.createElement("a");
    a.href = dataURL;
    a.download = useFormatFileName(
        chartName, //'itn'
        granularity.value,
        picked_date_start.value,
        picked_date_end.value,
        "png",
    );
    a.click();
}

function exportAsCSV() {
    if (!import.meta.client) return;
    const source = data.value?.time_series;
    if (!source) return;
    // const headers =
    const rows = source.map((row) => Object.values(row).join(",")).join("\n");

    const csv = `${headers}\n${rows}`;

    const a = document.createElement("a");
    a.href = `data:text/csv;charset=utf-8,${encodeURIComponent(csv)}`;
    a.download = useFormatFileName(
        chartName,
        granularity.value,
        picked_date_start.value,
        picked_date_end.value,
        "csv",
    );
    a.click();
}

function exportAsHTML() {
    if (!import.meta.client) return;
    const options = chartRef.value.getOption();
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
        chartName,
        granularity.value,
        picked_date_start.value,
        picked_date_end.value,
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
