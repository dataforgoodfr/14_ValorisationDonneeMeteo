<script setup lang="ts">
import { useItnStore } from "#imports";
import { storeToRefs } from "pinia";
import MonthPicker from "./monthPicker.vue";
import YearPicker from "./yearPicker.vue";
import DayPicker from "./dayPicker.vue";
import SliceType from "./sliceType.vue";
import ExportMenu from "../commons/exportMenu.vue";

const itnStore = useItnStore();
const { granularity, sliceTypeSwitchEnabled } = storeToRefs(useItnStore());

// Granularity Selection values
const granularityValues = reactive([
    { label: "Jour", value: "day" },
    { label: "Mois", value: "month" },
    { label: "Année", value: "year" },
]);
</script>

<template>
    <div
        id="select-bar-wrapper"
        class="flex flex-wrap gap-6 px-3 py-2 items-center"
    >
        <div
            id="left-side"
            class="flex flex-wrap gap-6 items-center self-stretch"
        >
            <UFormField label="Granularité" name="granularity">
                <USelect
                    :model-value="granularity"
                    :items="granularityValues"
                    name="granularity"
                    @update:model-value="itnStore.setGranularity"
                />
            </UFormField>

            <DayPicker v-if="granularity === 'day'" />
            <MonthPicker v-if="granularity === 'month'" />
            <YearPicker v-if="granularity === 'year'" />

            <USeparator
                orientation="vertical"
                size="sm"
                class="bg-gray-200 h-full self-stretch"
            />
        </div>

        <div id="right-side" class="flex flex-1 gap-6 items-center">
            <UTooltip
                :disabled="granularity !== 'day'"
                :disable-closing-trigger="true"
                arrow
                :delay-duration="0"
                text="Changez la Granularité pour activer cette option."
                :content="{
                    align: 'center',
                    side: 'top',
                    sideOffset: 8,
                }"
            >
                <span>
                    <USwitch
                        v-model="sliceTypeSwitchEnabled"
                        color="neutral"
                        :disabled="granularity === 'day'"
                        unchecked-icon="i-lucide-x"
                        checked-icon="i-lucide-check"
                        label="Type de moyenne"
                        :ui="{
                            root: 'flex-col justify-between text-center items-center',
                            container: 'my-auto',
                        }"
                        @update:model-value="itnStore.turnOffSliceType"
                    />
                </span>
            </UTooltip>

            <SliceType v-if="sliceTypeSwitchEnabled" />
            <ExportMenu class="ml-auto" />
        </div>
    </div>
</template>
