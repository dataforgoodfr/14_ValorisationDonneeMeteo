<script setup lang="ts">
const props = defineProps({
    title: { type: String, required: true },
    description: { type: String, required: true },
});
</script>

<template>
    <UPageHero :title="title" :description="description" />
</template>
