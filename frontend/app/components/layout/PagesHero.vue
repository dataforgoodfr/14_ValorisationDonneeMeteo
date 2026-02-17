<<<<<<< feat/#56_GenerateMockupDataFile
<script setup lang="ts"></script>

<template>
    <UPageHero :title="title" :description="description" />
=======
<script setup lang="ts">
const props = defineProps({
    title: { type: String, required: true },
    description: { type: String, required: true },
});
</script>

<template>
    <UPageHero
        :title="title"
        :description="description"
        :ui="{ container: 'py-12 sm:py-15 lg:py-17' }"
    />
>>>>>>> main
</template>
