<script setup lang="ts">
import type { NavigationMenuItem } from "@nuxt/ui";

const colorMode = useColorMode();
const toggleMode = (val: boolean) => {
    colorMode.preference = val ? "dark" : "light";
};

const route = useRoute();

const items = computed<NavigationMenuItem[]>(() => [
    {
        label: "Températures",
        children: [
            {
                label: "Écart à la normale",
                to: "/ecart-normale",
                icon: "i-lucide-move-horizontal",
                active: route.path.startsWith("/ecart-normale"),
            },
            {
                label: "Indicateur Thermique National",
                to: "/itn",
                icon: "i-lucide-thermometer-sun",
                active: route.path.startsWith("/itn"),
            },
            // {
            //     label: "Min/max",
            //     to: "/itn",
            //     icon: "i-lucide-diff",
            //     active: route.path.startsWith("/min-max"),
            // },
            {
                label: "Records",
                to: "/records",
                icon: "i-lucide-sun-snow",
                active: route.path.startsWith("/records"),
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
            <div class="flex gap-2 lg:mr-12">
                <UIcon name="i-lucide-hexagon" class="size-7" />
                <h1 class="font-title font-normal text-xl">DataClimat</h1>
            </div>
            <ULink to="/" class="text-lg">Accueil</ULink>
            <UNavigationMenu
                content-orientation="vertical"
                :items="items"
                :ui="{
                    content: 'w-max',
                    linkLabel: 'overflow-visible text-lg',
                    viewport: 'overflow-visible w-max',
                    viewportWrapper: 'overflow-visible w-max',
                    list: 'gap-2',
                    childLink: 'text-lg',
                }"
        /></template>

        <div class="flex justify-between">
            <UButton
                color="primary"
                variant="solid"
                class="px-8 text-lg"
                to="https://asso.infoclimat.fr/infos/formulaire.php"
                target="_blank"
                aria-label="infoclimat"
            >
                <span class="hidden lg:inline">Adhérer à InfoClimat</span>
                <span class="lg:hidden">Adhérer à InfoClimat</span>
            </UButton>
        </div>

        <template #right>
            <USwitch
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
        </template>

        <template #body>
            <UNavigationMenu
                :items="items"
                orientation="vertical"
                class="-mx-2.5"
            />
        </template>
    </UHeader>
</template>
