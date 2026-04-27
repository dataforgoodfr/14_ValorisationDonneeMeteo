<script setup lang="ts">
defineProps<{ text: string }>();
const isOpen = ref(false);
</script>

<template>
    <UPopover v-model:open="isOpen">
        <button
            class="size-3.5 text-muted hover:text-highlighted transition-colors cursor-pointer shrink-0"
            @mouseenter="isOpen = true"
            @mouseleave="isOpen = false"
        >
            <UIcon name="i-lucide-circle-help" class="size-full" />
        </button>
        <template #content>
            <p class="p-3 text-sm max-w-64">{{ text }}</p>
        </template>
    </UPopover>
</template>
