<script setup lang="ts">
import { useCustomDate } from "#imports";
import monthRangeDatePicker from "./monthRangeDatePicker.vue";
import type { CalendarDate } from "@internationalized/date";

const date = useCustomDate();
const selectState = reactive({
    date_start: date.lastYearYYYYMD.value,
    date_end: date.twoDaysAgoYYYMD.value,
    granularity: "month" as "year" | "month" | "day",
    slice_type: undefined as
        | undefined
        | "full"
        | "month_of_year"
        | "day_of_month",
    month_of_year: undefined as undefined | number,
    day_of_month: undefined as undefined | number,
});

// Granularity Selection
const granularity = ref([
    { label: "Jour", value: "day", disabled: true },
    { label: "Mois", value: "month" },
    { label: "Année", value: "year", disabled: true },
]);

const isMeanType = ref(false);

const meanType = ref([
    { label: "Jour", value: "day" },
    { label: "Mois", value: "month" },
    { label: "Année", value: "year" },
]);
const meanTypeValue = ref("");
</script>

<template>
    <div class="flex gap-6 px-3 py-2">
        <div id="main-filter" class="flex gap-6">
            <UFormField label="Granularité" name="granularity">
                <USelect
                    v-model="selectState.granularity"
                    :items="granularity"
                    name="granularity"
                />
            </UFormField>

            <monthRangeDatePicker
                :start-month="selectState.date_start"
                :end-month="selectState.date_end"
            />
            <USeparator
                orientation="vertical"
                class="w-px bg-gray-200 self-stretch"
            />
            <UButton type="submit"> Rafraichir </UButton>

            <USeparator
                orientation="vertical"
                class="w-px bg-gray-200 self-stretch"
            />
            <USwitch
                v-model="isMeanType"
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
                    v-model="meanTypeValue"
                    placeholder="Type de moyenne"
                    :items="meanType"
                />
            </UFormField>
        </div>
    </div>
</template>
