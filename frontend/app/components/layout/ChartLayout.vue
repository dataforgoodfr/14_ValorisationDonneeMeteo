<script setup lang="ts">
interface Props {
    hasSidebar?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
    hasSidebar: false,
});

const sidebarOpen = ref(false);
</script>

<template>
    <div
        class="flex w-full flex-col divide-y divide-gray-200 dark:divide-default border border-gray-200 dark:border-default rounded-lg overflow-hidden dark:bg-elevated"
    >
        <slot name="select-bar" />

        <div
            class="flex flex-col md:flex-row"
            :class="{
                'md:h-158 md:divide-x md:divide-gray-200 dark:md:divide-default':
                    props.hasSidebar,
            }"
        >
            <aside
                v-if="props.hasSidebar && $slots.sidebar"
                class="shrink-0 border-b border-gray-200 dark:border-default md:border-b-0"
            >
                <button
                    class="flex md:hidden w-full items-center justify-between px-4 py-2 text-sm font-medium text-gray-700 dark:text-default bg-gray-50 dark:bg-elevated"
                    @click="sidebarOpen = !sidebarOpen"
                >
                    <span>Sélection de stations</span>
                    <UIcon
                        name="i-lucide-chevron-down"
                        class="size-4 transition-transform duration-300"
                        :class="{ 'rotate-180': sidebarOpen }"
                    />
                </button>
                <Transition
                    enter-active-class="transition-all duration-300 ease-out overflow-hidden"
                    enter-from-class="opacity-0 -translate-y-2"
                    enter-to-class="opacity-100 translate-y-0"
                    leave-active-class="transition-all duration-200 ease-in overflow-hidden"
                    leave-from-class="opacity-100 translate-y-0"
                    leave-to-class="opacity-0 -translate-y-2"
                >
                    <div v-show="sidebarOpen" class="md:block! md:h-full">
                        <slot name="sidebar" />
                    </div>
                </Transition>
            </aside>

            <div class="flex-1 min-w-0 p-4">
                <slot name="chart" />
            </div>
        </div>
    </div>
</template>
