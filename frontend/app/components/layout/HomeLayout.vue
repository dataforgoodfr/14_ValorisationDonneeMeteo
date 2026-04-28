<script setup lang="ts">
import ImportantInformationSection from "~/components/home/ImportantInformationSection/ImportantInformationSection.vue";
import TodaySection from "~/components/home/TodaySection/TodaySection.vue";
import LastMonthSection from "~/components/home/Last30DaysSection/LastMonthSection.vue";
import LastYearSection from "~/components/home/Last365DaysSection/LastYearSection.vue";
</script>

<template>
    <div class="py-8">
        <h1
            class="font-extrabold text-4xl mb-2 text-blue-900 dark:text-blue-150"
        >
            Tableau de bord national
        </h1>
        <h2 class="mb-4 text-slate-500">
            Températures et anomalies — France métropolitaine
        </h2>
        <div class="flex flex-col gap-20">
            <div
                class="lg:grid lg:grid-cols-[2fr_1fr] gap-4 md:flex md:flex-col"
            >
                <ImportantInformationSection />
                <TodaySection />
            </div>
            <div class="lg:grid lg:grid-cols-2 gap-4 md:flex md:flex-col">
                <LastMonthSection />
                <LastYearSection />
            </div>
        </div>
    </div>
</template>
