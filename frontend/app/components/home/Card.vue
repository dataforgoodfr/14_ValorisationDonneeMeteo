<script setup lang="ts">
interface Props {
    title: string;
    tooltipText: string;
    withBorder?: boolean;
    showTitle?: boolean;
    transparent?: boolean;
    loading?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
    showTitle: true,
    transparent: false,
});
const isOpen = ref(false);
</script>
<template>
    <UCard
        :class="[
            'flex flex-col',
            props.withBorder && 'border border-blue-350',
            props.transparent && 'bg-transparent shadow-none ring-0',
        ]"
        :ui="{ body: props.transparent ? 'p-0' : '' }"
    >
        <template #default>
            <div
                v-if="props.showTitle"
                class="flex items-center justify-between pb-2"
            >
                <h1
                    class="text-sm font-semibold text-blue-700 dark:text-blue-350"
                >
                    {{ props.title }}
                </h1>
                <UPopover v-model:open="isOpen">
                    <button
                        class="text-blue-350 hover:text-blue-300 transition-colors cursor-pointer pl-2"
                        @mouseenter="isOpen = true"
                        @mouseleave="isOpen = false"
                    >
                        <UIcon name="i-lucide-circle-help" />
                    </button>
                    <template #content>
                        <p class="p-3 text-sm max-w-64">
                            {{ props.tooltipText }}
                        </p>
                    </template>
                </UPopover>
            </div>

            <template v-if="$slots.kpi">
                <UIcon
                    v-if="props.loading"
                    name="i-lucide-loader-circle"
                    class="animate-spin text-5xl text-muted"
                />
                <slot v-else name="kpi" />
            </template>

            <template v-if="$slots['kpi-context-box']">
                <USkeleton v-if="props.loading" class="h-5 w-full" />
                <div
                    v-else
                    class="kpi-context-box w-fit py-1 px-2 rounded-lg leading-none bg-amber-500 dark:bg-amber-700 border-amber-800 dark:border-amber-500 border"
                >
                    <span
                        class="text-xs font-medium text-amber-800 dark:text-amber-500"
                    >
                        <slot name="kpi-context-box" />
                    </span>
                </div>
            </template>

            <div v-if="$slots['kpi-context-text']" class="mt-3">
                <div
                    class="kpi-context-text text-xs text-slate-600 dark:text-slate-300 leading-none w-full"
                >
                    <USkeleton v-if="props.loading" class="h-2 w-full" />
                    <slot v-else name="kpi-context-text" />
                </div>
            </div>
            <div v-if="$slots['variation']" class="flex items-center mt-2">
                <div
                    class="text-xs text-blue-700 dark:text-blue-350 leading-none w-full"
                >
                    <USkeleton v-if="props.loading" class="h-2 w-full" />
                    <slot v-else name="variation" />
                </div>
            </div>
        </template>
    </UCard>
</template>

<style lang="css" scoped>
.kpi-context-text {
    font-family: Fira Code;
}
</style>
