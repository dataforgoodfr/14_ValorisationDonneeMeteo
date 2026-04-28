<template>
    <section class="flex flex-col gap-6">
        <p class="text-lg sm:text-xl/8 text-muted text-balance mt-6">
            Voici la liste des stations utilisées pour calculer cet indicateur
            thermique, et les poids associés dans le calcul de la moyenne.
        </p>
        <div class="flex gap-6 divide-x divide-gray-200 dark:divide-default">
            <ItnStationMap
                :stations="stations"
                :hovered-code="hoveredCode"
                @update:hovered-code="hoveredCode = $event"
            />
            <ItnStationList
                :stations="stations"
                :hovered-code="hoveredCode"
                @update:hovered-code="hoveredCode = $event"
            />
        </div>
    </section>
</template>

<script setup lang="ts">
import { ITN_STATIONS } from "~/constants/itn";
import ItnStationMap from "~/components/itn/ItnStationMap.vue";
import ItnStationList from "~/components/itn/ItnStationList.vue";

const hoveredCode = ref<string | null>(null);

const stations = ITN_STATIONS;
</script>
