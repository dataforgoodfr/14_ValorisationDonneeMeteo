<script setup lang="ts">
import { useBreakpoints, breakpointsTailwind } from "@vueuse/core";

interface InfoParagraph {
    title?: string;
    text: string;
}

interface InfoSection {
    label: string;
    content: string | InfoParagraph[];
}

interface Props {
    title: string;
    sections: InfoSection[];
}

const props = defineProps<Props>();

const isOpen = ref(false);
const breakpoints = useBreakpoints(breakpointsTailwind);
const isMobile = breakpoints.smaller("md");

const openSections = ref(new Set([0]));

function toggle(i: number) {
    if (openSections.value.has(i)) {
        openSections.value.delete(i);
    } else {
        openSections.value.add(i);
    }
    openSections.value = new Set(openSections.value);
}
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
                class="fixed right-0 top-0 h-full w-200 z-50 bg-dark-900 border-l border-dark-700 overflow-y-auto"
            >
                <div class="p-6 flex flex-col gap-1">
                    <div class="flex items-center justify-between mb-4">
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

                    <div
                        v-for="(section, i) in props.sections"
                        :key="section.label"
                        class="border-b border-dark-700 last:border-0"
                    >
                        <button
                            class="w-full flex items-center justify-between py-3 text-sm font-semibold text-dark-200 hover:text-white transition-colors cursor-pointer"
                            @click="toggle(i)"
                        >
                            {{ section.label }}
                            <UIcon
                                :name="
                                    openSections.has(i)
                                        ? 'i-lucide-chevron-up'
                                        : 'i-lucide-chevron-down'
                                "
                                class="size-4 shrink-0"
                            />
                        </button>
                        <div
                            v-show="openSections.has(i)"
                            class="pb-4 flex flex-col gap-3 text-sm text-dark-300"
                        >
                            <template v-if="Array.isArray(section.content)">
                                <div
                                    v-for="para in section.content"
                                    :key="para.title ?? para.text"
                                    class="flex flex-col gap-1"
                                >
                                    <p
                                        v-if="para.title"
                                        class="font-semibold text-dark-200"
                                    >
                                        {{ para.title }}
                                    </p>
                                    <p>{{ para.text }}</p>
                                </div>
                            </template>
                            <p v-else class="whitespace-pre-wrap">
                                {{ section.content }}
                            </p>
                        </div>
                    </div>
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
                <div class="p-5 flex flex-col gap-1">
                    <div class="flex items-center justify-between mb-4">
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

                    <div
                        v-for="(section, i) in props.sections"
                        :key="section.label"
                        class="border-b border-dark-700 last:border-0"
                    >
                        <button
                            class="w-full flex items-center justify-between py-3 text-sm font-semibold text-dark-200 hover:text-white transition-colors cursor-pointer"
                            @click="toggle(i)"
                        >
                            {{ section.label }}
                            <UIcon
                                :name="
                                    openSections.has(i)
                                        ? 'i-lucide-chevron-up'
                                        : 'i-lucide-chevron-down'
                                "
                                class="size-4 shrink-0"
                            />
                        </button>
                        <div
                            v-show="openSections.has(i)"
                            class="pb-4 flex flex-col gap-3 text-sm text-dark-300"
                        >
                            <template v-if="Array.isArray(section.content)">
                                <div
                                    v-for="para in section.content"
                                    :key="para.title ?? para.text"
                                    class="flex flex-col gap-1"
                                >
                                    <p
                                        v-if="para.title"
                                        class="font-semibold text-dark-200"
                                    >
                                        {{ para.title }}
                                    </p>
                                    <p>{{ para.text }}</p>
                                </div>
                            </template>
                            <p v-else class="whitespace-pre-wrap">
                                {{ section.content }}
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </Transition>
    </Teleport>
</template>
