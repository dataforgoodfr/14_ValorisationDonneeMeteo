<script setup lang="ts">
import AppFooter from "./components/layout/AppFooter.vue";
import AppHeader from "./components/layout/AppHeader.vue";
import { fr } from "@nuxt/ui/locale";
import { ECHART_DARK_THEME } from "~/constants/echartsTheme";

const colorMode = useColorMode();

const echartsTheme = computed(() =>
    colorMode.preference === "dark" ? ECHART_DARK_THEME : undefined,
);
provide(THEME_KEY, echartsTheme);
</script>

<template>
    <UApp :locale="fr" class="min-h-screen flex flex-col">
        <AppHeader />

        <UMain class="flex-1">
            <NuxtPage />
        </UMain>

        <AppFooter />
    </UApp>
</template>
