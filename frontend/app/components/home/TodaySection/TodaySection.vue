<script setup lang="ts">
import GoToDataLink from "../GoToDataLink.vue";
import ITNCard from "../ImportantInformationSection/ITNCard.vue";
import Section from "../Section.vue";

const today = new Date();
</script>
<template>
    <div>
        <Section :title="`AUJOURD'HUI - ${formatDateLongForDisplay(today)}`">
            <h2 class="text-blue-700 pb-2 dark:text-primary pb-2">
                MIN-MAX DU JOUR
            </h2>
            <div class="flex flex-col gap-2">
                <ITNCard />
                <ITNCard />
            </div>
            <GoToDataLink :data-url="'/itn'" />

            <div class="border-b to-slate-200" />

            <h2 class="text-blue-700 dark:text-primary pb-2 pt-1">
                RECORDS DE TEMPERATURE
            </h2>
            <div class="flex gap-2 md:flex-row flex-col">
                <ITNCard />
                <ITNCard />
            </div>
            <GoToDataLink :data-url="'/records'" />
        </Section>
    </div>
</template>
<style lang="css" scoped></style>
