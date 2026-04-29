<template>
    <section
        class="flex flex-col gap-4 dark:bg-elevated rounded-lg p-14 border border-gray-200 dark:border-default"
    >
        <p class="text-lg sm:text-xl/8 text-muted text-balance mb-6">
            Voici la liste des stations utilisées pour calculer cet indicateur
            thermique, et les poids associés dans le calcul de la moyenne.
        </p>
        <div class="flex justify-center flex-wrap gap-6">
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
