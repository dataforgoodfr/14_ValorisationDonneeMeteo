<script setup lang="ts">
import type { DropdownMenuItem } from "@nuxt/ui";
import Card from "./Card.vue";

interface Props {
    options?: DropdownMenuItem[];
    title: string;
    tooltipText: string;
    hotValue: number;
    coldValue: number;
    hotLabel?: string;
    coldLabel?: string;
    unitLabel?: string;
    variationContext?: string;
    withBorder?: boolean;
    variation?: number;
    pending?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
    options: undefined,
    hotLabel: "chaud",
    coldLabel: "froid",
    unitLabel: "records de",
    variationContext: "vs. 365 jours précédents",
    withBorder: false,
    variation: undefined,
    pending: false,
});

const total = computed(() => props.hotValue + props.coldValue);
const hotPercent = computed(() =>
    total.value > 0 ? Math.round((props.hotValue / total.value) * 100) : 0,
);
</script>

<template>
    <Card
        :title="props.title"
        :tooltip-text="props.tooltipText"
        :with-border="props.withBorder"
        class="h-fit max-w-96"
        :loading="props.pending"
    >
        <template #kpi>
            <div class="flex flex-wrap items-baseline gap-x-2 mb-1">
                <span class="font-semibold text-4xl text-red-400"
                    >{{ hotPercent }}%</span
                >
                <span
                    class="text-xs font-normal text-slate-500 dark:text-slate-300"
                >
                    de {{ props.unitLabel }} {{ props.hotLabel }}
                </span>
            </div>
            <div class="flex w-full h-4 rounded-full overflow-hidden mt-1 mb-2">
                <div
                    class="bg-red-400 transition-all duration-500"
                    :style="{ width: `${hotPercent}%` }"
                />
                <div class="bg-blue-400 flex-1" />
            </div>
        </template>
        <template v-if="props.variation !== undefined" #variation>
            <UIcon
                v-if="props.variation !== 0"
                :name="
                    props.variation <= 0
                        ? 'i-lucide-arrow-down-right'
                        : 'i-lucide-arrow-up-right'
                "
                :class="props.variation <= 0 ? 'text-blue-600' : 'text-red-450'"
                class="font-semibold"
            />
            <span
                v-if="props.variation !== 0"
                class="text-sm font-semibold"
                :class="props.variation < 0 ? 'text-blue-600' : 'text-red-450'"
            >
                {{ props.variation > 0 ? "+" : "" }}{{ props.variation }} points
            </span>
            <span v-else class="text-sm font-semibold text-blue-600"> = </span>
            {{ props.variationContext }}
        </template>
        <template #kpi-context-text>
            {{ props.hotValue }} {{ props.unitLabel }} {{ props.hotLabel }} vs
            {{ props.coldValue }} {{ props.unitLabel }} {{ props.coldLabel }}
        </template>
        <template v-if="props.options" #custom-export-button>
            <div class="flex justify-end mt-2">
                <UDropdownMenu
                    class="flex justify-end mt-2"
                    :items="props.options"
                    :content="{
                        align: 'start',
                        side: 'bottom',
                    }"
                >
                    <UButton
                        label="Exporter en csv"
                        size="xs"
                        icon="i-lucide-download"
                        :ui="{
                            base: 'bg-slate-450 ring-1 ring-blue-350 text-white',
                        }"
                    />
                </UDropdownMenu>
            </div>
        </template>
    </Card>
</template>
