<script setup lang="ts">
import Card from "./Card.vue";

interface Props {
    period?: string;
    title: string;
    tooltipText: string;
    compareTo: string;
    type?: "hot" | "cold";
    records: number;
    difference?: number;
}

const props = defineProps<Props>();
</script>
<template>
    <div class="min-w-56">
        <Card :title="props.title" :tooltip-text="props.tooltipText">
            <template #kpi>
                <span
                    class="text-4xl font-semibold"
                    :class="
                        props.type === 'hot' ? 'text-rose-600' : 'text-blue-600'
                    "
                    >{{ props.records }}</span
                >
                <span
                    :class="
                        props.type === 'hot' ? 'text-rose-600' : 'text-blue-600'
                    "
                >
                    records</span
                >
            </template>
            <template v-if="props.period" #kpi-context-text>
                {{ props.period }}
            </template>
            <template v-if="props.difference !== undefined" #variation>
                <UIcon
                    v-if="props.difference > 0"
                    :name="'i-lucide-arrow-up-right'"
                    class="text-blue-600"
                />
                <UIcon
                    v-if="props.difference < 0"
                    :name="'i-lucide-arrow-down-right'"
                    class="text-blue-600"
                />
                <span
                    class="text-sm font-semibold"
                    :class="
                        props.type === 'hot' ? 'text-rose-600' : 'text-blue-600'
                    "
                >
                    {{ props.difference !== 0 ? props.difference : "=" }}
                </span>
                <span class="text-sm"> vs {{ props.compareTo }} </span>
            </template>
        </Card>
    </div>
</template>
