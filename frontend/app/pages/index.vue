<!--
 Objectifs V0 :
 - Page d'accueil sans contenu
 - Dois simplement être wrappé par les Header + Footer (app.vue)
-->

<script setup lang="ts">
import type { ButtonProps } from "@nuxt/ui";

const heroLinks = ref<ButtonProps[]>([
    {
        label: "Détails de l'ITN",
        to: "/itn",
        color: "neutral",
    },
    {
        label: "Explorer une localisation",
        to: "/ecart-normale",
        color: "neutral",
    },
    {
        label: "Tester MapLibre",
        to: "/map-test",
        color: "neutral",
    },
]);
</script>

<template>
    <UContainer>
        <UPageHero
            headline="Aujourd'hui"
            title="Moy. nationale : --,-°C"
            description="+-,-°C par rapport à la moy. des 30 dernières années"
            :links="heroLinks"
            :ui="{
                wrapper: 'text-start',
                links: 'justify-normal',
                title: 'font-medium',
                headline:
                    'justify-normal text-slate-300 text-5xl sm:text-7xl text-pretty tracking-tight font-medium',
            }"
        />
    </UContainer>
</template>
