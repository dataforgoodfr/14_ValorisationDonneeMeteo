<script setup lang="ts">
import type { CalendarDate } from "@internationalized/date";
import { useCustomDate } from "~/composables/useCustomDate";

const date = useCustomDate();
const startMonth = defineModel<CalendarDate>("startMonth", { required: true }); // date.lastYearYYYYMD.value
const endMonth = defineModel<CalendarDate>("endMonth", { required: true }); // date.twoDaysAgoYYYMD.value
</script>

<template>
    <div class="flex items-center gap-1">
        <UFormField label="Date de début" name="date_start">
            <UPopover>
                <UButton color="neutral" variant="outline">
                    {{ date.monthYearDisplay(startMonth) }}
                </UButton>
                <template #content>
                    <UCalendar
                        v-model="startMonth"
                        class="p-2"
                        :prevent-deselect="true"
                        :month-controls="true"
                        :year-controls="true"
                        :min-value="date.absoluteMinDataDateYYYYMD"
                        :max-value="endMonth"
                    />
                </template>
            </UPopover>
        </UFormField>
        <div class="pt-7"><UIcon name="i-lucide-arrow-right" /></div>

        <UFormField label="Date de fin" name="date_end">
            <UPopover>
                <UButton color="neutral" variant="outline">
                    {{ date.monthYearDisplay(endMonth) }}
                </UButton>
                <template #content>
                    <UCalendar
                        v-model="endMonth"
                        class="p-2"
                        :prevent-deselect="true"
                        :month-controls="true"
                        :year-controls="true"
                        :min-value="startMonth"
                        :max-value="date.twoDaysAgoYYYMD.value"
                    />
                </template>
            </UPopover>
        </UFormField>
    </div>
</template>
