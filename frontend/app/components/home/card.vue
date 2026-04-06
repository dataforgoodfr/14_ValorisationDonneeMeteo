<script setup lang="ts">
interface Props {
    title: string;
    tooltipText: string;
}

const props = defineProps<Props>();
</script>
<template>
    <UCard class="w-55 border border-[#82C4E8]">
        <template #header>
            <div class="flex items-center justify-between">
                <h1 class="text-sm font-semibold">
                    {{ props.title }}
                </h1>
                <UTooltip v-if="props.tooltipText" :text="props.tooltipText">
                    <UIcon name="i-lucide-circle-question-mark" />
                </UTooltip>
            </div>
        </template>
        <template #default>
            <slot />
            <div class="kpi-context py-1 px-2 rounded-lg">
                <span class="text-xs font-medium text-gray-500 leading-none">
                    <slot name="kpi-context" />
                </span>
            </div>

            <slot name="footer" />
        </template>
    </UCard>
</template>

<style lang="css" scoped>
[data-slot="header"] {
    h1,
    span {
        color: #82c4e8;
    }
}
.kpi-context {
    background-color: #894b00;
    border: 1px solid #efb100;
    > span {
        color: #efb100;
    }
}
</style>
