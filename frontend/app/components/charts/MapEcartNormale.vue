<template>
    <ClientOnly>
        <div class="map-wrapper">
            <MglMap :map-style="style" :center="center" :zoom="zoom">
                <MglNavigationControl />
                <MglFullscreenControl />
                <MglGeolocateControl />
                <MglScaleControl />
            </MglMap>
        </div>
    </ClientOnly>
</template>

<script setup>
const style = "https://demotiles.maplibre.org/style.json";
const center = [1.8752, 46.6061];
const zoom = 5;
</script>

<style lang="css" scoped>
.map-wrapper {
    width: 100%;
    height: 800px;
}
</style>
