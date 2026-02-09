<script setup lang="ts">
import type { NavigationMenuItem } from "@nuxt/ui";

const route = useRoute();

const items = computed<NavigationMenuItem[]>(() => [
  {
    label: "Températures",
    icon: "material-symbols:thermostat",
    children: [
      {
        label: "Ecart à la normale",
        description: "Une description courte de la page",
        to: "/ecart-normale",
        icon: "i-lucide-move-horizontal",
        active: route.path.startsWith("/ecart-normale"),
      },
      {
        label: "Indicateur Thermique National",
        description: "Une description courte de la page",
        to: "/itn",
        icon: "i-lucide-thermometer-sun",
        active: route.path.startsWith("/itn"),
      },
      {
        disabled: true,
        label: "Min/max",
        description: "Bientôt disponible",
        to: "/itn",
        icon: "i-lucide-diff",
        // active: route.path.startsWith("/itn"),
      },
      {
        disabled: true,
        label: "Records",
        description: "Bientôt disponible",
        to: "/itn",
        icon: "i-lucide-sun-snow",
        // active: route.path.startsWith("/itn"),
      },
    ],
  },
  {
    disabled: true,
    label: "Pluviométrie",
    icon: "material-symbols:rainy-outline",
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
  <UHeader mode="slideover">
    <template #title>
      <h1>Infoclimat Dashboard</h1>
    </template>

    <UNavigationMenu
      content-orientation="vertical"
      :items="items"
      :ui="{ content: 'sm:w-80' }"
    />

    <template #right>
      <UTooltip text="Accedez au site InfoClimat">
        <UButton
          color="neutral"
          variant="outline"
          label="Tout InfoClimat"
          to="https://www.infoclimat.fr/"
          target="_blank"
          aria-label="infoclimat"
        />
      </UTooltip>
    </template>

    <template #body>
      <UNavigationMenu :items="items" orientation="vertical" class="-mx-2.5" />
    </template>
  </UHeader>
</template>
