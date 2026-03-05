<script setup lang="ts">
import type { DropdownMenuItem } from "@nuxt/ui";
import { useItnStore } from "#imports";

const itnStore = useItnStore();
const { itnChartRef, granularity, picked_date_start, picked_date_end } =
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
    },
    {
        label: "Format HTML",
        icon: "i-lucide-file-code",
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
    a.download = `${useFormatFileName(`${granularity.value}`, `${picked_date_start.value.toISOString().substring(0, 10)} to ${picked_date_end.value.toISOString().substring(0, 10)}`, "itn")}.png`;
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
