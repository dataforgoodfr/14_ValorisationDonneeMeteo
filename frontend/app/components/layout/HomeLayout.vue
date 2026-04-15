<script setup lang="ts">

import ImportantInformationSection from "../home/ImportantInformation/index.vue";
import TodaySection from "../home/TodaySection/index.vue";
import LastMonthSection from "../home/Last30DaysSection/index.vue";
import LastYearSection from "../home/Last365DaysSection/index.vue";
</script>
<template>
    <div class="py-8">
        <h1 class="font-extrabold text-4xl mb-2">Tableau de bord national</h1>
        <h2 class="mb-4">Températures et anomalies — France métropolitaine</h2>
        <div class="flex flex-col gap-20">
          <div class="lg:grid lg:grid-cols-[2fr_1fr] gap-4 md:flex md:flex-col">
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
