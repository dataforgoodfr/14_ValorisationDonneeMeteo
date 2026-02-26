<script setup lang="ts">
import { useCustomDate } from "~/composables/useCustomDate";

const date = useCustomDate();
const startMonth = shallowRef(date.lastYearYYYYMD.value);
const endMonth = shallowRef(date.twoDaysAgoYYYMD.value);
</script>

<template>
    <div class="flex items-center gap-1">
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
        <UIcon name="i-lucide-arrow-right" />
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
    </div>
</template>
