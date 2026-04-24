<script setup lang="ts">
import {
    ATTRIBUTION_TEXT,
    ATTRIBUTION_FONT_SIZE,
} from "~/constants/chartAttribution";
import { COLORS } from "~/constants/colors";

const lines = ATTRIBUTION_TEXT.split("\n");
</script>

<template>
    <div
        class="pointer-events-none text-right leading-tight"
        :style="{
            fontSize: `${ATTRIBUTION_FONT_SIZE}px`,
            color: COLORS.foreground,
        }"
    >
        <div v-for="line in lines" :key="line">{{ line }}</div>
    </div>
</template>
