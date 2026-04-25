<script setup lang="ts">
import Section from "../Section.vue";
import ITNCard from "../ImportantInformationSection/ITNCard.vue";
import GoToDataLink from "../GoToDataLink.vue";

const { yesterday, yesterdayLess365Days } = useCustomDate();
</script>

<template>
    <div>
        <Section
            :title="`CES 365 DERNIERS JOURS -  ${formatDateLongForDisplay(yesterdayLess365Days)} au ${formatDateLongForDisplay(yesterday)}`"
        >
            <h2 class="text-blue-700 dark:text-primary pb-2">
                INDICATEUR THERMIQUE NATIONAL
            </h2>
            <div class="flex flex-col gap-2">
                <ITNCard />
                <ITNCard />
            </div>
            <GoToDataLink :data-url="'/itn'" />
            <div class="border-b to-dark-200" />
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
