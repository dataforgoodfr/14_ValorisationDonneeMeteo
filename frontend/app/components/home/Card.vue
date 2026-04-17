<script setup lang="ts">
interface Props {
    title: string;
    tooltipText: string;
}

const props = defineProps<Props>();
</script>
<template>
    <UCard class="border border-blue-350 flex flex-col">
        <template #default>
            <div class="flex items-center justify-between pb-2">
                <h1 class="text-sm font-semibold text-blue-350">
                    {{ props.title }}
                </h1>
                <UTooltip :text="props.tooltipText" class="text-blue-350">
                    <UIcon name="i-lucide-circle-question-mark" />
                </UTooltip>
            </div>

            <slot name="kpi" />
            <div
                v-if="$slots['kpi-context-box']"
                class="kpi-context-box py-1 px-2 rounded-lg leading-none bg-amber-700 border-amber-500 border"
            >
                <span class="text-xs font-medium text-amber-500">
                    <slot name="kpi-context-box" />
                </span>
            </div>
            <div v-if="$slots['kpi-context-text']" class="mt-2">
                <span
                    class="kpi-context-text text-xs text-slate-300 leading-none"
                >
                    <slot name="kpi-context-text" />
                </span>
            </div>
            <div v-if="$slots['variation']" class="flex items-center mt-1">
                <span class="text-xs text-blue-350">
                    <slot name="variation" />
                </span>
            </div>
        </template>
    </UCard>
</template>

<style lang="css" scoped>
.kpi-context-text {
    font-family: Fira Code;
}
</style>
