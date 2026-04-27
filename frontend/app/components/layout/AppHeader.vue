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
        :ui="{ left: 'lg:flex-initial', title: 'lg:flex-initial' }"
    >
        <template #title>
            <div class="flex gap-2 mr-12">
                <UIcon name="i-lucide-hexagon" class="size-7" />
                <h1 class="font-title font-normal">DataClimat</h1>
            </div>
        </template>
        <template #default>
            <UNavigationMenu
                content-orientation="vertical"
                :items="items"
                :ui="{
                    content: 'w-max',
                    link: 'border rounded-md',
                    linkLabel: 'overflow-visible',
                    viewport: 'overflow-visible w-max',
                    viewportWrapper: 'overflow-visible w-max',
                    list: 'gap-2',
                }"
            />
        </template>

        <template #right>
            <UTooltip text="Accedez au site Infoclimat.fr">
                <UButton
                    color="neutral"
                    variant="outline"
                    label="Site Infoclimat.fr"
                    to="https://www.infoclimat.fr/"
                    target="_blank"
                    aria-label="infoclimat"
                />
            </UTooltip>
            <USwitch
                unchecked-icon="i-lucide-sun"
                checked-icon="i-lucide-moon"
                aria-label="Basculer le thème"
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
