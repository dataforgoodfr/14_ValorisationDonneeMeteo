<script setup lang="ts">
import GoToDataLink from "../GoToDataLink.vue";
import ITNCard from "../ImportantInformationSection/ITNCard.vue";
import Section from "../Section.vue";

const { yesterday, yesterdayLess30Days } = useCustomDate();
</script>

<template>
    <div>
        <Section
            :title="`CES 30 DERNIERS JOURS -  ${formatDateLongForDisplay(yesterdayLess30Days)} au ${formatDateLongForDisplay(yesterday)}`"
        >
            <h2 class="text-blue-700 dark:text-primary pb-2">
                ECART DE TEMPERATURE A LA NORMALE
            </h2>
            <div class="flex flex-col gap-2">
                <ITNCard />
                <ITNCard />
            </div>
            <GoToDataLink :data-url="'/ecart-normale'" />
            <div class="border-b to-slate-200" />
            <h2 class="text-blue-700 dark:text-primary pb-2 pt-1">
                RECORDS DE TEMPERATURE
            </h2>
            <div class="flex gap-2">
                <ITNCard />
                <ITNCard />
            </div>
            <GoToDataLink :data-url="'/records'" />
        </Section>
    </div>
</template>
