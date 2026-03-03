<script setup lang="ts">
import { useItnStore } from "#imports";
import { storeToRefs } from "pinia";
import MonthPicker from "./monthPicker.vue";
import YearPicker from "./yearPicker.vue";
import DayPicker from "./dayPicker.vue";

const { granularity, slice_type } = storeToRefs(useItnStore());

const isMeanType = ref(false);

// Granularity Selection values
const granularityValues = reactive([
    { label: "Jour", value: "day" },
    { label: "Mois", value: "month" },
    { label: "Année", value: "year" },
]);

// Slice Type Selection values
const sliceTypeValues = reactive([
    { label: "Jour", value: "day" },
    { label: "Mois", value: "month" },
    { label: "Année", value: "year" },
]);
</script>

<template>
    <div class="flex gap-6 px-3 py-2">
        <div id="main-filter" class="flex gap-6">
            <UFormField label="Granularité" name="granularity">
                <USelect
                    v-model="granularity"
                    :items="granularityValues"
                    name="granularity"
                />
            </UFormField>

            <DayPicker v-if="granularity === 'day'" />
            <MonthPicker v-if="granularity === 'month'" />
            <YearPicker v-if="granularity === 'year'" />

            <USeparator
                orientation="vertical"
                class="w-px bg-gray-200 self-stretch"
            />
            <USwitch
                v-model="isMeanType"
                disabled
                unchecked-icon="i-lucide-x"
                checked-icon="i-lucide-check"
                label="Type de moyenne"
                :ui="{
                    root: 'flex-col justify-between text-center items-center',
                    container: 'my-auto',
                }"
            />

            <UFormField
                v-if="isMeanType"
                label="Type de moyenne"
                name="slice_type"
            >
                <USelect
                    v-model="slice_type"
                    placeholder="Type de moyenne"
                    :items="sliceTypeValues"
                />
            </UFormField>
        </div>
    </div>
</template>
