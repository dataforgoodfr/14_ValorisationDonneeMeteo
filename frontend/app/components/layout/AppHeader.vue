<script setup lang="ts">
import type { NavigationMenuItem } from "@nuxt/ui";

const route = useRoute();

const items = computed<NavigationMenuItem[]>(() => [
    {
        label: "Températures",
        children: [
            {
                label: "Ecart à la normale",
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
            {
                disabled: true,
                label: "Min/max",
                to: "/itn",
                icon: "i-lucide-diff",
                // active: route.path.startsWith("/itn"),
            },
            {
                label: "Records",
                to: "/records",
                icon: "i-lucide-sun-snow",
                active: route.path.startsWith("/records"),
            },
        ],
    },
    {
        disabled: true,
        label: "Pluviométrie",
        children: [
            {
                //To be filled
            },
            {
                //To be filled
            },
        ],
    },
]);
</script>

<template>
    <UHeader
        mode="slideover"
        title="InfoClimat"
        :ui="{ left: 'lg:flex-initial', title: 'lg:flex-initial' }"
    >
        <template #title>
            <div class="flex gap-2 mr-12">
                <UIcon name="i-lucide-hexagon" class="size-7" />
                <h1 class="font-title font-normal">Infoclimat</h1>
            </div>
        </template>
        <template #default>
            <UNavigationMenu
                content-orientation="vertical"
                :items="items"
                :ui="{
                    content: 'min-w-fit',
                    link: 'border border-default rounded-md text-black',
                    list: 'gap-2',
                }"
            />
        </template>

        <template #right>
            <UTooltip text="Accedez au site InfoClimat">
                <UButton
                    color="neutral"
                    variant="outline"
                    icon="i-lucide-cloud-sun-rain"
                    label="Tout InfoClimat"
                    to="https://www.infoclimat.fr/"
                    target="_blank"
                    aria-label="infoclimat"
                />
            </UTooltip>
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
