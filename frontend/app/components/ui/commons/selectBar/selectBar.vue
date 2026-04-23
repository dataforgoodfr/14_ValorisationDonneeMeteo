<script setup lang="ts">
import MonthPicker from "./monthPicker.vue";
import YearPicker from "./yearPicker.vue";
import StackedYearPicker from "./stackedYearPicker.vue";
import DayPicker from "./dayPicker.vue";
import SliceType from "./sliceType.vue";
import RecordsPeriodSlice from "./recordsPeriodSlice.vue";
import ExportMenu from "~/components/ui/commons/exportMenu.vue";
import type {
    GranularityType,
    SelectBarAdapter,
} from "~/components/ui/commons/selectBar/types";
import SelectChartType from "~/components/ui/commons/selectBar/selectChartType.vue";

interface Props {
    adapter: SelectBarAdapter;
}

const props = defineProps<Props>();

provide("selectBarAdapter", props.adapter);

const localStartDate = props.adapter.pickedDateStart;
const localEndDate = props.adapter.pickedDateEnd;
const dates = useCustomDate();

// Granularity Selection values
const granularityValues = computed(() => [
    { label: "Jour", value: "day" },
    { label: "Mois", value: "month" },
    {
        label: "Année",
        value: "year",
        disabled: props.adapter.chartType?.value === "stacked",
    },
]);
</script>

<template>
    <div
        id="select-bar-wrapper"
        class="flex flex-col md:flex-row md:flex-wrap gap-4 px-3 py-2 items-start md:items-center"
    >
        <div
            id="left-side"
            class="flex flex-wrap gap-4 items-center md:self-stretch"
        >
            <UFormField label="Granularité" name="granularity">
                <USelect
                    :model-value="adapter.granularity.value"
                    :items="granularityValues"
                    name="granularity"
                    @update:model-value="
                        (item) =>
                            adapter.setGranularity(item as GranularityType)
                    "
                />
            </UFormField>

            <template v-if="adapter.chartType?.value !== 'stacked'">
                <DayPicker
                    v-if="adapter.granularity.value === 'day'"
                    v-model:start-date="localStartDate"
                    v-model:end-date="localEndDate"
                    :min-date="dates.absoluteMinDataDate.value"
                    :max-date="dates.today.value"
                />
                <MonthPicker
                    v-if="adapter.granularity.value === 'month'"
                    v-model:start-date="localStartDate"
                    v-model:end-date="localEndDate"
                    :min-date="dates.absoluteMinDataDate.value"
                    :max-date="dates.today.value"
                />
                <YearPicker
                    v-if="adapter.granularity.value === 'year'"
                    v-model:start-date="localStartDate"
                    v-model:end-date="localEndDate"
                    :min-date="dates.absoluteMinDataDate.value"
                    :max-date="dates.today.value"
                />
            </template>
            <StackedYearPicker v-if="adapter.chartType?.value === 'stacked'" />
            <SelectChartType v-if="adapter.features.hasChartTypeSelector" />

            <USeparator
                orientation="vertical"
                size="sm"
                class="hidden md:block bg-gray-200 h-full self-stretch"
            />
        </div>

        <div id="right-side" class="flex flex-1 gap-6 items-center">
            <template
                v-if="
                    (adapter.features.hasSliceType &&
                        adapter.chartType?.value !== 'calendar' &&
                        adapter.chartType?.value !== 'stacked') ||
                    adapter.features.hasRecordsPeriodSlice
                "
            >
                <UTooltip
                    :disabled="adapter.granularity.value !== 'day'"
                    :disable-closing-trigger="true"
                    :arrow="true"
                    :delay-duration="0"
                    text="Changez la Granularité pour activer cette option."
                    :content="{
                        align: 'center',
                        side: 'top',
                        sideOffset: 8,
                    }"
                >
                    <span class="flex h-14">
                        <USwitch
                            v-model="adapter.sliceTypeSwitchEnabled!.value"
                            color="neutral"
                            :disabled="adapter.granularity.value === 'day'"
                            unchecked-icon="i-lucide-x"
                            checked-icon="i-lucide-check"
                            :label="
                                adapter.sliceTypeSwitchLabel ?? 'Moyenne par'
                            "
                            :ui="{
                                root: 'flex-col-reverse items-center gap-1',
                                container: 'my-auto',
                            }"
                            @update:model-value="adapter.turnOffSliceType"
                        />
                    </span>
                </UTooltip>

                <SliceType
                    v-if="
                        adapter.sliceTypeSwitchEnabled?.value &&
                        adapter.features.hasSliceType
                    "
                />
                <RecordsPeriodSlice
                    v-if="
                        adapter.sliceTypeSwitchEnabled?.value &&
                        adapter.features.hasRecordsPeriodSlice
                    "
                />
            </template>
            <ExportMenu v-if="adapter.features.hasExport" class="ml-auto" />
        </div>
    </div>
</template>
