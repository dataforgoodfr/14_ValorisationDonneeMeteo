<script setup lang="ts">
interface Props {
    hasSidebar?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
    hasSidebar: false,
});
</script>

<template>
    <div
        class="inline-flex flex-col divide-y divide-gray-200 border border-gray-200 rounded-lg overflow-hidden"
    >
        <slot name="select-bar" />

        <div
            class="flex"
            :class="{
                'h-158 divide-x divide-gray-200': props.hasSidebar,
            }"
        >
            <aside v-if="props.hasSidebar && $slots.sidebar" class="shrink-0">
                <slot name="sidebar" />
            </aside>

            <div class="flex-1 min-w-0 px-3 py-2">
                <slot name="chart" />
            </div>
        </div>
    </div>
</template>
