<script setup lang="ts">
import { useBreakpoints, breakpointsTailwind } from "@vueuse/core";

interface Props {
    title: string;
}

const props = defineProps<Props>();

const isOpen = ref(false);
const breakpoints = useBreakpoints(breakpointsTailwind);
const isMobile = breakpoints.smaller("md");
</script>

<template>
    <button
        class="fixed bottom-6 right-6 z-30 flex items-center justify-center size-10 rounded-full bg-blue-500 text-white shadow-lg hover:bg-blue-450 transition-colors cursor-pointer"
        :aria-label="`Informations sur ${props.title}`"
        @click="isOpen = true"
    >
        <UIcon name="i-lucide-info" class="size-5" />
    </button>

    <Teleport to="body">
        <Transition
            enter-active-class="transition-opacity duration-300"
            enter-from-class="opacity-0"
            enter-to-class="opacity-100"
            leave-active-class="transition-opacity duration-200"
            leave-from-class="opacity-100"
            leave-to-class="opacity-0"
        >
            <div
                v-if="isOpen"
                class="fixed inset-0 z-40 bg-black/50"
                @click="isOpen = false"
            />
        </Transition>

        <Transition
            enter-active-class="transition-transform duration-300 ease-out"
            enter-from-class="translate-x-full"
            enter-to-class="translate-x-0"
            leave-active-class="transition-transform duration-200 ease-in"
            leave-from-class="translate-x-0"
            leave-to-class="translate-x-full"
        >
            <div
                v-if="isOpen && !isMobile"
                class="fixed right-0 top-0 h-full w-96 z-50 bg-dark-900 border-l border-dark-700 overflow-y-auto"
            >
                <div class="p-6 flex flex-col gap-5">
                    <div class="flex items-center justify-between">
                        <h2 class="text-base font-semibold text-dark-200">
                            {{ props.title }}
                        </h2>
                    </div>
                    <slot />
                </div>
            </div>
        </Transition>

        <Transition
            enter-active-class="transition-all duration-300 ease-out"
            enter-from-class="opacity-0 scale-95"
            enter-to-class="opacity-100 scale-100"
            leave-active-class="transition-all duration-200 ease-in"
            leave-from-class="opacity-100 scale-100"
            leave-to-class="opacity-0 scale-95"
        >
            <div
                v-if="isOpen && isMobile"
                class="fixed inset-x-4 top-1/2 -translate-y-1/2 z-50 max-h-[80vh] overflow-y-auto rounded-xl bg-dark-900 border border-dark-700"
            >
                <div class="p-5 flex flex-col gap-5">
                    <div class="flex items-center justify-between">
                        <h2 class="text-base font-semibold text-dark-200">
                            {{ props.title }}
                        </h2>
                        <button
                            class="text-dark-400 hover:text-dark-200 transition-colors cursor-pointer"
                            aria-label="Fermer"
                            @click="isOpen = false"
                        >
                            <UIcon name="i-lucide-x" class="size-5" />
                        </button>
                    </div>
                    <slot />
                </div>
            </div>
        </Transition>
    </Teleport>
</template>
