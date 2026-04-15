<script setup lang="ts">
interface Props {
    title: string;
    tooltipText: string;
}

const props = defineProps<Props>();
</script>
<template>
    <UCard class="border border-[#82C4E8] flex flex-col">
        <template #header>
            <div class="flex items-center justify-between">
                <h1 class="text-sm font-semibold">
                    {{ props.title }}
                </h1>
                <UTooltip :text="props.tooltipText">
                    <UIcon name="i-lucide-circle-question-mark" />
                </UTooltip>
            </div>
        </template>
        <template #default>
            <slot name="kpi" />
            <div
                v-if="$slots['kpi-context-box']"
                class="kpi-context-box py-1 px-2 rounded-lg leading-none"
            >
                <span class="text-xs font-medium text-gray-500">
                    <slot name="kpi-context-box" />
                </span>
            </div>
            <div v-if="$slots['kpi-context-text']" class="mt-2">
                <span
                    class="kpi-context-text text-xs text-gray-500 leading-none"
                >
                    <slot name="kpi-context-text" />
                </span>
            </div>
            <div v-if="$slots['variation']" class="flex items-center mt-1">
                <span class="blue text-xs">
                    <slot name="variation" />
                </span>
            </div>
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
.kpi-context-box {
    background-color: #894b00;
    border: 1px solid #efb100;
    > span {
        color: #efb100;
    }
}

.kpi-context-text {
    color: #90a1b9;
    font-family: Fira Code;
}
</style>
