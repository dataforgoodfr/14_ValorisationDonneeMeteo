<script setup lang="ts">
import { CalendarDate } from "@internationalized/date";
import { useItnStore } from "~/stores/itnStore";
import { storeToRefs } from "pinia";
import { useCustomDate } from "#imports";

const inputDate = useTemplateRef("inputDate");

const itnStore = useItnStore();
const { picked_date_start, picked_date_end } = storeToRefs(itnStore);

const dates = useCustomDate();

// Reset to day 1 of the selected month
const handleUpdateStartDate = () => {
    const { year, month } = picked_date_start.value;
    picked_date_start.value = new CalendarDate(year, month, 1);
};

const handleUpdateEndDate = () => {
    const { year, month } = picked_date_end.value;
    picked_date_end.value = new CalendarDate(year, month, 1);
};
onMounted(() => {
    handleUpdateStartDate();
    handleUpdateEndDate();
});
</script>

<template>
    <div id="container-monthly-picker" class="flex gap-2">
        <div id="start-date-picker" class="flex flex-col text-center gap-1">
            <p class="text-sm text-default">Mois de début</p>
            <UInputDate
                ref="inputDate"
                v-model="picked_date_start"
                :min-value="dates.absoluteMinDataDateYYYYMD.value"
                :max-value="picked_date_end"
                :ui="{
                    base: 'h-fit',
                    segment: 'data-[segment=day]:hidden nth-2:hidden',
                }"
                @update:start-value="handleUpdateStartDate"
                @update:model-value="handleUpdateStartDate"
            >
                <template #trailing>
                    <UPopover :reference="inputDate?.inputsRef[3]?.$el">
                        <UButton
                            color="neutral"
                            variant="link"
                            size="sm"
                            icon="i-lucide-calendar"
                            aria-label="Select a date"
                            class="px-0"
                        />

                        <template #content>
                            <UCalendar
                                v-model="picked_date_start"
                                :prevent-deselect="true"
                                :min-value="
                                    dates.absoluteMinDataDateYYYYMD.value
                                "
                                :max-value="picked_date_end"
                                class="p-2"
                                @update:start-value="handleUpdateStartDate"
                                @update:model-value="handleUpdateStartDate"
                            />
                        </template>
                    </UPopover>
                </template>
            </UInputDate>
        </div>

        <div class="pt-7"><UIcon name="i-lucide-arrow-right" /></div>

        <div id="start-date-picker" class="flex flex-col text-center gap-1">
            <p class="text-sm text-default">Mois de fin</p>
            <UInputDate
                ref="inputDate"
                v-model="picked_date_end"
                :min-value="picked_date_start"
                :max-value="dates.twoDaysAgoYYYMD.value"
                :ui="{
                    base: 'h-fit',
                    segment: 'data-[segment=day]:hidden nth-2:hidden',
                }"
                @update:model-value="handleUpdateEndDate"
                @update:start-value="handleUpdateEndDate"
            >
                <template #trailing>
                    <UPopover :reference="inputDate?.inputsRef[3]?.$el">
                        <UButton
                            color="neutral"
                            variant="link"
                            size="sm"
                            icon="i-lucide-calendar"
                            aria-label="Select a date"
                            class="px-0"
                        />

                        <template #content>
                            <UCalendar
                                v-model="picked_date_end"
                                :prevent-deselect="true"
                                :min-value="picked_date_start"
                                :max-value="dates.twoDaysAgoYYYMD.value"
                                class="p-2"
                                @update:model-value="handleUpdateEndDate"
                                @update:start-value="handleUpdateEndDate"
                            />
                        </template>
                    </UPopover>
                </template>
            </UInputDate>
        </div>
    </div>
</template>
