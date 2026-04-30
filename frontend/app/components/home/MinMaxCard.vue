<script setup lang="ts">
import { UIcon } from "#components";
import { dateToStringDMY } from "#imports";

interface Props {
    hotCold: "hot" | "cold";
    temperature?: string;
    date?: Date;
    city?: string;
    departmentString?: string;
    departmentNumber?: number;
}

const props = defineProps<Props>();

const tagData = computed(() => {
    if (props.hotCold === "hot") {
        return {
            icon: "i-lucide-sun",
            text: "CHAUD",
            class: "text-error-600 bg-error-200",
            placeholderClass: "text-error-200 bg-error-200",
        };
    }
    return {
        icon: "i-lucide-snowflake",
        text: "FROID",
        class: "text-secondary-600 bg-secondary-200",
        placeholderClass: "text-secondary-200-200 bg-secondary-200",
    };
});
</script>
<template>
    <UCard class="w-fit min-w-64" :ui="{ body: 'flex flex-col' }">
        <div
            id="upper-card"
            :class="`${tagData.class} text-[13px] self-start flex gap-1 items-center rounded-lg p-1 font-semibold`"
        >
            <UIcon :name="tagData.icon" class="text-[15px]" />
            <span>{{ tagData.text }}</span>
        </div>
        <div
            v-if="temperature"
            id="lower-card"
            class="flex items-center justify-start gap-2"
        >
            <div id="lower-left" class="text-dimmed text-xs">#1</div>
            <div id="lower-center">
                <p class="font-bold">{{ city.toUpperCase() }}</p>
                <p class="text-dimmed text-xs">
                    {{ departmentString }} ·
                    {{ departmentNumber }}
                </p>
            </div>
            <div id="lower-right" class="flex flex-col gap-1 ml-auto items-end">
                <div
                    :class="`${tagData.class} rounded-lg py-1 px-4 text-center `"
                >
                    {{ temperature }}°C
                </div>
                <div class="text-dimmed text-xs">
                    {{ dateToStringDMY(date) }}
                </div>
            </div>
        </div>
        <div v-else class="text-xs italic py-4">
            Données bientôt disponible.
        </div>
    </UCard>
</template>
