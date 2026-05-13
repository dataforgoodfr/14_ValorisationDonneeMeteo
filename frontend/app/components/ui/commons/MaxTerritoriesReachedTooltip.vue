<script setup lang="ts">
import { MAX_GRAPH_TERRITORIES } from "~/constants/graphSelection";

defineProps<{ isAtLimit: boolean }>();
</script>
<template>
    <UTooltip
        :disabled="!isAtLimit"
        :disable-closing-trigger="true"
        :arrow="true"
        :delay-duration="0"
        :text="`${MAX_GRAPH_TERRITORIES} graphes maximum peuvent être affichés, veuillez supprimer un des choix sélectionné`"
        :content="{ align: 'center', side: 'top', sideOffset: 8 }"
    >
        <div class="overflow-y-auto">
            <div :class="{ 'pointer-events-none opacity-50': isAtLimit }">
                <slot />
            </div>
        </div>
    </UTooltip>
</template>
