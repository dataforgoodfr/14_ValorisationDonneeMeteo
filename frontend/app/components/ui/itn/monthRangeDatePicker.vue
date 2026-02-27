<script setup lang="ts">
import { useItnStore } from "~/stores/itnStore";
import { storeToRefs } from "pinia";
import { useCustomDate } from "#imports";

const itnStore = useItnStore();
const { picked_date_start, picked_date_end } = storeToRefs(itnStore);

const dates = useCustomDate();
</script>

<template>
    <div class="flex items-center gap-1">
        <UFormField label="Date de début" name="picked_date_start">
            <UPopover>
                <UButton color="neutral" variant="outline">
                    {{ dates.monthYearDisplay(picked_date_start) }}
                </UButton>
                <template #content>
                    <UCalendar
                        v-model="picked_date_start"
                        class="p-2"
                        :prevent-deselect="true"
                        :month-controls="true"
                        :year-controls="true"
                        :min-value="dates.absoluteMinDataDateYYYYMD.value"
                        :max-value="picked_date_end"
                    />
                </template>
            </UPopover>
        </UFormField>
        <div class="pt-7"><UIcon name="i-lucide-arrow-right" /></div>

        <UFormField label="Date de fin" name="picked_date_end">
            <UPopover>
                <UButton color="neutral" variant="outline">
                    {{ dates.monthYearDisplay(picked_date_end) }}
                </UButton>
                <template #content>
                    <UCalendar
                        v-model="picked_date_end"
                        class="p-2"
                        :prevent-deselect="true"
                        :month-controls="true"
                        :year-controls="true"
                        :min-value="picked_date_start"
                        :max-value="dates.twoDaysAgoYYYMD.value"
                    />
                </template>
            </UPopover>
        </UFormField>
    </div>
</template>
