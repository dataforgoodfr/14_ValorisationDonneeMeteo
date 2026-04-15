<script setup lang="ts">
import type { ButtonProps } from "@nuxt/ui";
import ImportantInformationSection from "~/components/home/ImportantInformationSection.vue";

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
        <ImportantInformationSection />
    </UContainer>
</template>
