<script setup lang="ts">
import type { NavigationMenuItem } from "@nuxt/ui";

const route = useRoute();

const items = computed<NavigationMenuItem[]>(() => [
  {
    label: "Températures",
    icon: "material-symbols:thermostat",
    children: [
      {
        label: "Ecarts à la normale",
        description: "Une description courte de la page",
        to: "/ecart-normale",
        icon: "material-symbols:arrow-range-rounded",
        active: route.path.startsWith("/ecart-normale"),
      },
      {
        label: "Indicateurs thermique",
        description: "Une description courte de la page",
        to: "/indicateurs-thermique",
        icon: "material-symbols:thermostat-arrow-up",
        active: route.path.startsWith("/indicateurs-thermique"),
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
  <UHeader>
    <template #title>
      <h1>Infoclimat Dashboard</h1>
    </template>

    <template #default>
      <UNavigationMenu content-orientation="vertical" :items="items" />
    </template>

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
  </UHeader>
</template>
