<script setup lang="ts">
import { EXPORT_BTN_UI } from "~/constants/tableUtils";

defineProps<{ hasActiveFilters: boolean }>();
const emit = defineEmits<{ reset: [] }>();
</script>

<template>
    <div class="flex flex-col items-center gap-3 py-8 text-muted">
        <span>Aucune donnée affichée.</span>
        <UButton
            v-if="hasActiveFilters"
            label="Réinitialiser les filtres"
            icon="i-lucide-filter-x"
            :ui="EXPORT_BTN_UI"
            @click="emit('reset')"
        />
    </div>
</template>
