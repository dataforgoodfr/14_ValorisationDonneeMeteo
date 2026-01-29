<script setup lang="ts">
import AppFooter from "./components/layout/AppFooter.vue";
import AppHeader from "./components/layout/AppHeader.vue";
</script>

<template>
  <UApp class="min-h-screen flex flex-col">
    <AppHeader />

    <UMain class="flex-1">
      <NuxtPage />
    </UMain>

    <AppFooter />
  </UApp>
</template>
