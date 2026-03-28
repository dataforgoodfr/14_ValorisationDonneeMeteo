<script setup lang="ts">
defineProps<{
    /** Current minimum bound (empty string means no bound set). */
    min: string;
    /** Current maximum bound (empty string means no bound set). */
    max: string;
    /** When true, shows the "Effacer" button. */
    hasFilter: boolean;
}>();

const emit = defineEmits<{
    "update:min": [value: string];
    "update:max": [value: string];
    clear: [];
}>();
</script>

<template>
    <div class="p-3 flex flex-col gap-3">
        <div class="flex flex-col gap-1">
            <label class="text-xs font-medium text-muted">Minimum</label>
            <UInput
                type="number"
                :model-value="min"
                size="sm"
                placeholder="Min"
                @update:model-value="emit('update:min', String($event))"
            />
        </div>
        <div class="flex flex-col gap-1">
            <label class="text-xs font-medium text-muted">Maximum</label>
            <UInput
                type="number"
                :model-value="max"
                size="sm"
                placeholder="Max"
                @update:model-value="emit('update:max', String($event))"
            />
        </div>
        <button
            v-if="hasFilter"
            class="text-xs text-error hover:underline text-left"
            @click="emit('clear')"
        >
            Effacer
        </button>
    </div>
</template>
