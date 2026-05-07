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
import FieldInfo from "~/components/ui/commons/FieldInfo.vue";

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

// Calendar averaging options
const calendarAveragingOptions = computed(() => {
    if (props.adapter.granularity.value === "year") {
        return [
            { label: "Année", value: "no" },
            { label: "Mois", value: "yes" },
        ];
    }
    return [
        { label: "Mois", value: "no" },
        { label: "Jour", value: "yes" },
    ];
});
</script>

<template>
    <div
        id="select-bar-wrapper"
        class="flex flex-col md:flex-row md:flex-wrap gap-4 px-3 py-2 items-start md:items-center"
    >
        <!-- Paramètres d'affichage -->
        <div class="flex flex-col gap-1">
            <div class="flex items-center gap-1">
                <span class="font-medium text-default">
                    Paramètres d'affichage
                </span>
                <FieldInfo
                    text="Sélectionnez la résolution temporelle et l'intervalle de temps affichés sur le graphe."
                />
            </div>
            <div class="flex flex-wrap gap-4 items-center">
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
                    <div class="flex flex-col gap-0.5">
                        <span class="font-medium text-default">
                            Dates limites affichées
                        </span>
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
                    </div>
                </template>
                <StackedYearPicker
                    v-if="adapter.chartType?.value === 'stacked'"
                />
                <SelectChartType v-if="adapter.features.hasChartTypeSelector" />
            </div>
        </div>

        <USeparator
            orientation="vertical"
            size="sm"
            class="hidden md:block bg-gray-200 md:self-stretch"
        />

        <!-- Paramètre d'analyse + Export -->
        <div class="flex flex-1 gap-6 items-center flex-wrap">
            <template
                v-if="
                    (adapter.features.hasSliceType &&
                        adapter.chartType?.value !== 'calendar' &&
                        adapter.chartType?.value !== 'stacked') ||
                    adapter.features.hasRecordsPeriodSlice
                "
            >
                <div class="flex flex-col gap-1">
                    <div class="flex items-center gap-1">
                        <span class="font-medium text-default">
                            Paramètre d'analyse
                        </span>
                        <FieldInfo
                            v-if="adapter.analysisPeriodInfoText"
                            :text="adapter.analysisPeriodInfoText"
                        />
                    </div>
                    <div class="flex gap-6 items-center">
                        <SliceType v-if="adapter.features.hasSliceType" />
                        <RecordsPeriodSlice
                            v-if="adapter.features.hasRecordsPeriodSlice"
                        />
                    </div>
                </div>
            </template>
            <template
                v-if="
                    adapter.features.hasSliceType &&
                    adapter.chartType?.value === 'calendar' &&
                    adapter.granularity.value !== 'day'
                "
            >
                <div class="flex flex-col gap-1">
                    <div class="flex items-center gap-1">
                        <span class="font-medium text-default">
                            Paramètre d'analyse
                        </span>
                    </div>
                    <div class="flex gap-6 items-center">
                        <div class="flex flex-col text-center gap-1">
                            <p class="text-sm text-default">Moyenner par</p>
                            <USelect
                                :model-value="
                                    adapter.calendarAverageEnabled?.value
                                        ? 'yes'
                                        : 'no'
                                "
                                :items="calendarAveragingOptions"
                                @update:model-value="
                                    (val) => {
                                        adapter.calendarAverageEnabled!.value =
                                            val === 'yes';
                                        adapter.setCalendarAverageEnabled?.(
                                            val === 'yes',
                                        );
                                    }
                                "
                            />
                        </div>
                        <SliceType
                            v-if="adapter.calendarAverageEnabled?.value"
                        />
                    </div>
                </div>
            </template>

            <ExportMenu v-if="adapter.features.hasExport" class="md:ml-auto" />
        </div>
    </div>
</template>
