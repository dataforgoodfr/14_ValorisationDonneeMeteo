<!--
 Objectifs V0 :
 - A Réaliser : https://github.com/dataforgoodfr/14_ValorisationDonneeMeteo/issues/4
-->

<script setup lang="ts">
const config = useRuntimeConfig();
// just testing that the frontend can reach the backend api
const { data: records, pending, error } = await useFetch(config.public.apiBase);

console.log("Données reçues :", records.value);
</script>

<template>
  <UContainer>
    <h1>Page Indicateur Thermique National</h1>
  </UContainer>
</template>
