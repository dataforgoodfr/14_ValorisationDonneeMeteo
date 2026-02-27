<script setup lang="ts">
import { useItnStore } from "~/stores/itnStore";
import { storeToRefs } from "pinia";
import { useCustomDate } from "#imports";

const inputDate = useTemplateRef("inputDate");

const itnStore = useItnStore();
const { picked_date_start, picked_date_end } = storeToRefs(itnStore);

const dates = useCustomDate();
</script>

<template>
    <div id="container-daily-picker" class="flex gap-2">
        <div id="start-date-picker" class="flex flex-col text-center gap-1">
            <p class="text-sm text-default">Date de début</p>
            <UInputDate
                ref="inputDate"
                v-model="picked_date_start"
                :min-value="dates.absoluteMinDataDateYYYYMD.value"
                :max-value="picked_date_end"
                :ui="{
                    base: 'h-fit',
                }"
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
                            />
                        </template>
                    </UPopover>
                </template>
            </UInputDate>
        </div>

        <div class="pt-7"><UIcon name="i-lucide-arrow-right" /></div>

        <div id="start-date-picker" class="flex flex-col text-center gap-1">
            <p class="text-sm text-default">Date de fin</p>
            <UInputDate
                ref="inputDate"
                v-model="picked_date_end"
                :min-value="picked_date_start"
                :max-value="dates.twoDaysAgoYYYMD.value"
                :ui="{
                    base: 'h-fit',
                }"
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
                            />
                        </template>
                    </UPopover>
                </template>
            </UInputDate>
        </div>
    </div>
</template>
