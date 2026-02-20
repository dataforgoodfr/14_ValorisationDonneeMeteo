<!--
 Objectifs V0 :
 - A Réaliser : tester l'intégration de nuxt-maplibre au sein du projet, en affichant une carte centrée sur la France
-->

<script setup lang="ts">
import PagesHero from "~/components/layout/PagesHero.vue";
import MapsSimpleMap from "~/components/maps/SimpleMap.vue";

const heroData = {
    title: "Test de l'intégration de MapLibre",
    description:
        "Tester l'intégration de nuxt-maplibre au sein du projet, en affichant une carte centrée sur la France",
};
</script>

<template>
    <UContainer class="flex flex-col gap-y-16">
        <PagesHero
            :title="heroData.title"
            :description="heroData.description"
        />
        <div>
            <MapsSimpleMap />
        </div>
    </UContainer>
</template>

<style scoped>
.map-test-page {
    padding: 20px;
}

h1 {
    margin-bottom: 20px;
}
</style>
