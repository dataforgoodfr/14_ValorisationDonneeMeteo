<script setup lang="ts">
import Card from "./Card.vue";

interface Props {
    title: string;
    tooltipText: string;
    hotValue: number;
    coldValue: number;
    hotLabel?: string;
    coldLabel?: string;
    withBorder?: boolean;
    variation?: number;
}

const props = withDefaults(defineProps<Props>(), {
    hotLabel: "chaud",
    coldLabel: "froid",
    withBorder: false,
    variation: undefined,
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
    >
        <template #kpi>
            <p class="font-semibold text-4xl mb-1 text-red-400">
                {{ hotPercent }}%
                <span
                    class="text-sm font-normal text-slate-500 dark:text-slate-300"
                >
                    de records de {{ props.hotLabel }}
                </span>
            </p>
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
                :name="
                    props.variation <= 0
                        ? 'i-lucide-arrow-down-right'
                        : 'i-lucide-arrow-up-right'
                "
                :class="props.variation <= 0 ? 'text-blue-600' : 'text-red-450'"
                class="font-semibold"
            />
            <span
                class="text-sm font-semibold"
                :class="props.variation <= 0 ? 'text-blue-600' : 'text-red-450'"
            >
                {{ props.variation > 0 ? "+" : "" }}{{ props.variation }} points
            </span>
            vs. période précédente
        </template>
        <template #kpi-context-text>
            {{ props.hotValue }} records de {{ props.hotLabel }} vs
            {{ props.coldValue }} records de {{ props.coldLabel }}
        </template>
    </Card>
</template>
