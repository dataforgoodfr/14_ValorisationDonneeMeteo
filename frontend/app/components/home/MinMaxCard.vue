<script setup lang="ts">
import { UIcon } from "#components";
import { dateToStringDMY } from "#imports";

interface Props {
    hotCold: "hot" | "cold";
    temperature: string | undefined;
    date: Date;
    city: string | undefined;
}

const props = defineProps<Props>();

const sunIceTagData = computed(() => {
    if (props.hotCold === "hot") {
        return {
            icon: "i-lucide-sun",
            text: "CHAUD",
            class: "text-error-600 bg-error-200",
        };
    }
    return {
        icon: "i-lucide-snowflake",
        text: "FROID",
        class: "text-secondary-600 bg-secondary-200",
    };
});
</script>
<template>
    <UCard
        class="border border-blue-350 flex flex-col max-w-96 dark:bg-dark-850"
        :ui="{ body: 'flex flex-col' }"
    >
        <div
            id="upper-card"
            :class="`${sunIceTagData.class} text-[13px] self-start flex gap-1 items-center rounded-lg p-1 font-semibold`"
        >
            <UIcon :name="sunIceTagData.icon" class="text-[15px]" />
            <span>{{ sunIceTagData.text }}</span>
        </div>
        <div id="lower-card" class="flex items-center justify-start gap-2">
            <div id="lower-left" class="text-dimmed text-xs">#1</div>
            <div id="lower-center">
                <p class="font-bold">{{ city }}</p>
                <p class="text-dimmed text-xs">Savoie · 73</p>
            </div>
            <div id="lower-right" class="flex flex-col gap-1 ml-auto items-end">
                <div
                    :class="`${sunIceTagData.class} rounded-lg py-1 px-4 text-center `"
                >
                    {{ temperature }}°C
                </div>
                <div class="text-dimmed text-xs">
                    {{ dateToStringDMY(date) }}
                </div>
            </div>
        </div>
    </UCard>
</template>
