<script setup lang="ts">
import type { NavigationMenuItem } from "@nuxt/ui";

const colorMode = useColorMode();
const toggleMode = (val: boolean) => {
    colorMode.preference = val ? "dark" : "light";
};

const route = useRoute();

const items = computed<NavigationMenuItem[]>(() => [
    {
        label: "Accueil",
        to: "/",
    },
    {
        label: "Températures",
        children: [
            {
                label: "Écart à la normale",
                to: "/temperature/ecart-normale",
                icon: "i-lucide-move-horizontal",
                active: route.path.startsWith("/temperature/ecart-normale"),
            },
            {
                label: "Indicateur Thermique National",
                to: "/temperature/itn",
                icon: "i-lucide-thermometer-sun",
                active: route.path.startsWith("/temperature/itn"),
            },
            // {
            //     label: "Min/max",
            //     to: "/temperature/itn",
            //     icon: "i-lucide-diff",
            //     active: route.path.startsWith("/temperature/min-max"),
            // },
            {
                label: "Records",
                to: "/temperature/records",
                icon: "i-lucide-sun-snow",
                active: route.path.startsWith("/temperature/records"),
            },
        ],
    },
    {
        label: "Doc & FAQ",
        children: [
            {
                label: "Documentation",
                to: "/doc_et_faq/doc",
                icon: "i-lucide-book-open",
                active: route.path.startsWith("/doc_et_faq/doc"),
            },
            {
                label: "FAQ",
                to: "/doc_et_faq/faq",
                icon: "i-lucide-circle-help",
                active: route.path.startsWith("/doc_et_faq/faq"),
            },
        ],
    },
    {
        label: "À propos",
        children: [
            {
                label: "Qui sommes nous ?",
                to: "/a-propos/qui-sommes-nous",
                icon: "i-lucide-users",
                active: route.path.startsWith("/a-propos/qui-sommes-nous"),
            },
            {
                label: "Le projet collaboratif",
                to: "/a-propos/le-projet",
                icon: "i-lucide-lightbulb",
                active: route.path.startsWith("/a-propos/le-projet"),
            },
        ],
    },
]);
</script>

<template>
    <UHeader
        mode="slideover"
        title="DataClimat"
        :ui="{
            left: 'flex-1 gap-7',
            center: 'flex-1 justify-center',
            right: 'flex items-center',
        }"
    >
        <template #left>
            <ULink
                to="/"
                class="'shrink-0 font-bold text-xl text-highlighted flex items-end gap-1.5'"
            >
                <div class="flex gap-2 lg:mr-12">
                    <UIcon name="i-lucide-hexagon" class="size-7" />
                    <h1 class="font-title font-normal text-xl">DataClimat</h1>
                </div>
            </ULink>

            <UNavigationMenu
                variant="link"
                content-orientation="vertical"
                class="hidden lg:flex"
                :items="items"
                :ui="{
                    content: 'w-max',
                    linkLabel: 'overflow-visible text-lg',
                    viewport: 'overflow-visible w-max',
                    viewportWrapper: 'overflow-visible w-max',
                    list: 'gap-2',
                    childLink: 'text-lg',
                    childList: 'dark:bg-dark-850',
                }"
        /></template>

        <div class="flex justify-between">
            <!-- Commenter le temps de la beta (jusqu'au 22/05/2026) -->
            <!-- :ui="{ base: 'bg-slate-450 ring-1 ring-blue-350 text-white' }" to="https://asso.infoclimat.fr/infos/formulaire.php" target="_blank" -->

            <UButton
                :ui="{
                    base: 'bg-orange-500 ring-1 ring-orange-350 text-white',
                }"
                class="px-8 text-lg"
                aria-label="infoclimat"
            >
                <!-- Commenter le temps de la beta (jusqu'au 22/05/2026) -->
                <!-- <span class="hidden lg:inline">Adhérer à Infoclimat</span>
                <span class="lg:hidden">Adhérer à Infoclimat</span> -->
                <span class="hidden lg:inline"
                    >Version Beta: certaines données sont inexactes</span
                >
                <span class="lg:hidden"
                    >Version Beta: certaines données sont inexactes</span
                >
            </UButton>
        </div>

        <template #right>
            <USwitch
                unchecked-icon="i-lucide-sun"
                checked-icon="i-lucide-moon"
                aria-label="Basculer le thème"
                size="xl"
                class="hidden lg:flex"
                :ui="{
                    base: 'dark:bg-transparent dark:ring-1 dark:ring-white/20',
                    thumb: 'dark:bg-black',
                }"
                @update:model-value="toggleMode"
            />
        </template>

        <template #body>
            <div class="flex flex-col gap-6">
                <USwitch
                    class="self-end"
                    unchecked-icon="i-lucide-sun"
                    checked-icon="i-lucide-moon"
                    aria-label="Basculer le thème"
                    size="xl"
                    :ui="{
                        base: 'dark:bg-transparent dark:ring-1 dark:ring-white/20',
                        thumb: 'dark:bg-black',
                    }"
                    @update:model-value="toggleMode"
                />
                <UNavigationMenu
                    :items="items"
                    orientation="vertical"
                    class="-mx-2.5"
                    :ui="{
                        content: 'w-max',
                        linkLabel: 'overflow-visible text-lg',
                        viewport: 'overflow-visible w-max',
                        viewportWrapper: 'overflow-visible w-max',
                        list: 'gap-2',
                        childLink: 'text-lg',
                        childList: 'dark:bg-dark-850',
                    }"
                />
                <!-- Commenter le temps de la beta (jusqu'au 22/05/2026) -->
                <!-- :ui="{
                        base: 'bg-slate-450 ring-1 ring-blue-350 text-white',
                    }"
                    to="https://asso.infoclimat.fr/infos/formulaire.php"
                    target="_blank" -->

                <UButton
                    :ui="{
                        base: 'bg-orange-600 ring-1 ring-orange-350 text-white',
                    }"
                    class="self-center px-8 text-lg mt-8"
                    aria-label="infoclimat"
                >
                    <!-- Commenter le temps de la beta (jusqu'au 22/05/2026) -->
                    <!-- <span class="hidden lg:inline">Adhérer à Infoclimat</span>
                    <span class="lg:hidden">Adhérer à Infoclimat</span> -->
                    <span class="hidden lg:inline"
                        >Version Beta: certaines données sont inexactes</span
                    >
                    <span class="lg:hidden"
                        >Version Beta: certaines données sont inexactes</span
                    >
                </UButton>
            </div>
        </template>
    </UHeader>
</template>
