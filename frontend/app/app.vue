<script setup lang="ts">
import { InitMockupData } from "~~/public/ChartDataProvider";
import AppFooter from "./components/layout/AppFooter.vue";
import AppHeader from "./components/layout/AppHeader.vue";
import { fr } from "@nuxt/ui/locale";

InitMockupData()
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
