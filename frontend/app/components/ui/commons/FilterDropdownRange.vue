<script setup lang="ts">
const props = defineProps<{
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

function onUpdateMin(value: string) {
    if (props.max && value && Number(value) > Number(props.max)) return;
    emit("update:min", value);
}

function onUpdateMax(value: string) {
    if (props.min && value && Number(value) < Number(props.min)) return;
    emit("update:max", value);
}
</script>

<template>
    <div class="p-3 flex flex-col gap-3">
        <div class="flex flex-col gap-1">
            <label class="text-xs font-medium text-muted">Minimum</label>
            <UInput
                type="number"
                :model-value="min"
                :max="max || undefined"
                size="sm"
                placeholder="Min"
                @update:model-value="onUpdateMin(String($event))"
            />
        </div>
        <div class="flex flex-col gap-1">
            <label class="text-xs font-medium text-muted">Maximum</label>
            <UInput
                type="number"
                :model-value="max"
                :min="min || undefined"
                size="sm"
                placeholder="Max"
                @update:model-value="onUpdateMax(String($event))"
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
