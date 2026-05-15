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

const { isOpen } = useInfoPanel();
const breakpoints = useBreakpoints(breakpointsTailwind);
const isMobile = breakpoints.smaller("md");

const openSections = ref(new Set([0]));
const showHint = ref(false);
const isBouncing = ref(false);

function toggle(i: number) {
    if (openSections.value.has(i)) {
        openSections.value.delete(i);
    } else {
        openSections.value.add(i);
    }
    openSections.value = new Set(openSections.value);
}

function dismissHint() {
    showHint.value = false;
    isBouncing.value = false;
    sessionStorage.setItem("info-hint-dismissed", "1");
}

function openPanel() {
    dismissHint();
    isOpen.value = true;
}

let t1: ReturnType<typeof setTimeout>;
let t2: ReturnType<typeof setTimeout>;
let t3: ReturnType<typeof setTimeout>;

onMounted((): void => {
    if (sessionStorage.getItem("info-hint-dismissed")) return;

    t1 = setTimeout(() => {
        isBouncing.value = true;
        showHint.value = true;
    }, 10_000);
    t2 = setTimeout(() => {
        isBouncing.value = false;
    }, 13_000);
    t3 = setTimeout(() => {
        showHint.value = false;
    }, 16_000);
});

onUnmounted((): void => {
    clearTimeout(t1);
    clearTimeout(t2);
    clearTimeout(t3);
});
</script>

<template>
    <Transition
        enter-active-class="transition-all duration-300 ease-out"
        enter-from-class="opacity-0 translate-y-1"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition-all duration-200 ease-in"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 translate-y-1"
    >
        <div
            v-if="showHint"
            class="fixed bottom-[4.5rem] right-6 z-30 w-44 rounded-lg bg-white dark:bg-dark-800 border border-slate-200 dark:border-dark-700 shadow-lg px-3 py-2"
        >
            <div class="flex items-start justify-between gap-2">
                <p class="text-xs text-slate-700 dark:text-dark-200">
                    Besoin d'informations ? Cliquez ici pour en savoir plus.
                </p>
                <button
                    class="shrink-0 text-slate-400 hover:text-slate-600 dark:text-dark-400 dark:hover:text-dark-200 transition-colors cursor-pointer"
                    aria-label="Fermer"
                    @click="dismissHint"
                >
                    <UIcon name="i-lucide-x" class="size-3" />
                </button>
            </div>
            <div
                class="absolute -bottom-1.5 right-3.5 size-3 rotate-45 bg-white dark:bg-dark-800 border-r border-b border-slate-200 dark:border-dark-700"
            />
        </div>
    </Transition>

    <button
        :class="[
            'fixed bottom-6 right-6 z-30 flex items-center justify-center size-10 rounded-full bg-blue-500 text-white shadow-lg hover:bg-blue-450 transition-colors cursor-pointer',
            isBouncing && 'animate-bounce',
        ]"
        :aria-label="`Informations sur ${props.title}`"
        @click="openPanel"
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
                class="fixed right-0 top-0 h-full w-200 z-50 bg-white dark:bg-dark-900 border-l border-slate-200 dark:border-dark-700 overflow-y-auto"
            >
                <div class="p-6 flex flex-col gap-1">
                    <div class="flex items-center justify-between mb-4">
                        <h2
                            class="text-base font-semibold text-blue-700 dark:text-dark-200"
                        >
                            {{ props.title }}
                        </h2>
                        <button
                            class="text-blue-700 hover:text-blue-900 dark:text-dark-400 dark:hover:text-dark-200 transition-colors cursor-pointer"
                            aria-label="Fermer"
                            @click="isOpen = false"
                        >
                            <UIcon name="i-lucide-x" class="size-5" />
                        </button>
                    </div>

                    <div
                        v-for="(section, i) in props.sections"
                        :key="section.label"
                        class="border-b border-slate-200 dark:border-dark-700 last:border-0"
                    >
                        <button
                            class="w-full flex items-center justify-between py-3 text-sm font-semibold text-blue-700 hover:text-blue-900 dark:text-dark-200 dark:hover:text-white transition-colors cursor-pointer"
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
                            class="pb-4 flex flex-col gap-3 text-sm text-blue-700 dark:text-dark-300"
                        >
                            <template v-if="Array.isArray(section.content)">
                                <div
                                    v-for="para in section.content"
                                    :key="para.title ?? para.text"
                                    class="flex flex-col gap-1"
                                >
                                    <p
                                        v-if="para.title"
                                        class="font-semibold text-blue-700 dark:text-dark-200"
                                    >
                                        {{ para.title }}
                                    </p>
                                    <p class="whitespace-pre-wrap">
                                        {{ para.text }}
                                    </p>
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
                                    <p class="whitespace-pre-wrap">
                                        {{ para.text }}
                                    </p>
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
