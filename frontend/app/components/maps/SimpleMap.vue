<template>
    <ClientOnly>
        <div ref="mapContainer" class="map-wrapper"></div>
    </ClientOnly>
</template>

<script setup lang="ts">
import maplibregl from "maplibre-gl";

const mapContainer = ref<HTMLElement | null>(null);
let map: maplibregl.Map | null = null;

onMounted(async () => {
    await nextTick();

    if (mapContainer.value) {
        try {
            map = new maplibregl.Map({
                container: mapContainer.value,
                style: "https://demotiles.maplibre.org/style.json",
                center: [2.3522, 48.8566],
                zoom: 4,
            });
        } catch (error) {
            console.error("Error creating map:", error);
        }
    }
});

onUnmounted(() => {
    if (map) {
        map.remove();
    }
});
</script>

<style scoped>
.map-wrapper {
    width: 100%;
    height: 600px;
}
</style>
