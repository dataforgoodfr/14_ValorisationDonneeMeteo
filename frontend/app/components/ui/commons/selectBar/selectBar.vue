<script setup lang="ts">
import MonthPicker from "./monthPicker.vue";
import YearPicker from "./yearPicker.vue";
import DayPicker from "./dayPicker.vue";
import SliceType from "./sliceType.vue";
import ExportMenu from "../exportMenu.vue";
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
                    :model-value="adapter.granularity.value"
                    :items="granularityValues"
                    name="granularity"
                    @update:model-value="
                        (item) =>
                            adapter.setGranularity(item as GranularityType)
                    "
                />
            </UFormField>

            <DayPicker
                v-if="adapter.granularity.value === 'day'"
                v-model:start-date="localStartDate"
                v-model:end-date="localEndDate"
                :min-date="dates.absoluteMinDataDate.value"
                :max-date="dates.twoDaysAgo.value"
            />
            <MonthPicker v-if="adapter.granularity.value === 'month'" />
            <YearPicker v-if="adapter.granularity.value === 'year'" />
            <SelectChartType v-if="adapter.features.hasChartTypeSelector" />

            <USeparator
                orientation="vertical"
                size="sm"
                class="bg-gray-200 h-full self-stretch"
            />
        </div>

        <div id="right-side" class="flex flex-1 gap-6 items-center">
            <template v-if="adapter.features.hasSliceType">
                <UTooltip
                    :disabled="adapter.granularity.value !== 'day'"
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
                    <span class="flex h-14">
                        <USwitch
                            v-model="adapter.sliceTypeSwitchEnabled!.value"
                            color="neutral"
                            :disabled="adapter.granularity.value === 'day'"
                            unchecked-icon="i-lucide-x"
                            checked-icon="i-lucide-check"
                            label="Moyenne par"
                            :ui="{
                                root: 'flex-col-reverse items-center gap-1',
                                container: 'my-auto',
                            }"
                            @update:model-value="adapter.turnOffSliceType"
                        />
                    </span>
                </UTooltip>

                <SliceType v-if="adapter.sliceTypeSwitchEnabled?.value" />
            </template>
            <ExportMenu v-if="adapter.features.hasExport" class="ml-auto" />
        </div>
    </div>
</template>
