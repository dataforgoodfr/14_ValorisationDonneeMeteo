<script setup lang="ts">
defineProps<{ text: string }>();
</script>

<template>
    <UTooltip
        :text="text"
        :content="{ side: 'top', align: 'center', sideOffset: 6 }"
        :arrow="true"
    >
        <UIcon
            name="i-lucide-info"
            class="size-3.5 text-muted hover:text-highlighted transition-colors cursor-help shrink-0"
        />
    </UTooltip>
</template>
