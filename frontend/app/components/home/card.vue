<script setup lang="ts">
interface Props {
    title: string;
    tooltipText: string;
}

const props = defineProps<Props>();
</script>
<template>
    <div>
        <UCard class="max-w-220">
            <header>
                <h1 class="text-sm font-semibold">
                    {{ props.title }}
                </h1>
                <UTooltip :text="props.tooltipText">
                    <UIcon name="i-lucide-circle-question-mark" />
                </UTooltip>
            </header>
            <slot />
            <div class="context-content py-1 px-2 rounded-lg">
                <span class="text-sm text-gray-500">
                    <slot name="context-content" />
                </span>
            </div>
            <div>
                <slot name="footer" />
            </div>
        </UCard>
    </div>
</template>

<style lang="css" scoped>
header {
    align-items: center;
    display: flex;
    justify-content: space-between;

    h1 {
        color: #82c4e8;
    }
}
.context-content {
    background-color: rgba(137, 75, 0, 0.4);
    border-color: #efb100;
    > span {
        color: #efb100;
    }
}
</style>
