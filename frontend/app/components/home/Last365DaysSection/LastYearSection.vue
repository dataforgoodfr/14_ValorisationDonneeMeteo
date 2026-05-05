<script setup lang="ts">
import Section from "../Section.vue";
import GoToDataLink from "../GoToDataLink.vue";
import RecordsRatioCard from "./RecordsRatioCard.vue";
import Itn365Cards from "./Itn365Cards.vue";
// import ExtremeCard from "../ExtremeCard.vue";

const { yesterday, yesterdayLess365Days } = useCustomDate();
</script>

<template>
    <Section
        :title="`CES 365 DERNIERS JOURS -  ${formatDateLongForDisplay(yesterdayLess365Days)} au ${formatDateLongForDisplay(yesterday)}`"
    >
        <h2 class="text-blue-700 dark:text-primary pb-2">
            INDICATEUR THERMIQUE NATIONAL
        </h2>
        <Itn365Cards />
        <GoToDataLink :data-url="'/itn'" />

        <div class="border-b to-dark-200" />
        <h2 class="text-blue-700 dark:text-primary pb-2 pt-1">
            RECORDS DE TEMPERATURE
        </h2>
        <div class="flex gap-6 justify-center items-center">
            <RecordsRatioCard class="flex-1" />
            <!-- commenter en attendant l'implémentation -->
            <!-- <div class="flex flex-col gap-2 w-fit">
                <ExtremeCard hot-cold="hot" :disabled="true" />
                <ExtremeCard hot-cold="cold" :disabled="true" />
            </div> -->
        </div>
        <GoToDataLink :data-url="'/records'" />
    </Section>
</template>
