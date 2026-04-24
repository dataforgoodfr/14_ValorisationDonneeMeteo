<script setup lang="ts">
import AppFooter from "./components/layout/AppFooter.vue";
import AppHeader from "./components/layout/AppHeader.vue";
import { fr } from "@nuxt/ui/locale";
import { ECHART_DARK_THEME } from "~/utils/echartsTheme";

const colorMode = useColorMode();
colorMode.value = "dark";
colorMode.preference = "light";

if (colorMode.value === "dark") {
    provide(THEME_KEY, ECHART_DARK_THEME);
}
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
