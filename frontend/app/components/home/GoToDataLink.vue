<script setup lang="ts">
const props = defineProps<{
    dataUrl: string;
}>();
</script>
<template>
    <ULink
        as="button"
        :to="props.dataUrl"
        class="flex items-center gap-2 text-blue-450 font-semibold justify-end pt-3 pb-1"
    >
        <span>Accéder aux données</span>
        <UIcon name="i-lucide-arrow-right" />
    </ULink>
</template>
