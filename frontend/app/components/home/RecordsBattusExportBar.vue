<script setup lang="ts">
const props = defineProps<{
    dateStart: string;
    dateEnd: string;
}>();

const { exportRecords } = useExportRecordsBattus();
</script>

<template>
    <div class="flex gap-4">
        <ULink
            as="button"
            class="flex items-start gap-0 text-red-500 font-semibold pt-3 pb-1 max-w-52"
            @click="exportRecords('hot', props.dateStart, props.dateEnd)"
        >
            <UIcon name="i-lucide-download" class="shrink-0 mt-0.5" />
            <span>Exporter la liste des records de chaleur</span>
        </ULink>
        <ULink
            as="button"
            class="flex items-start gap-0 text-blue-500 font-semibold pt-3 pb-1 max-w-52"
            @click="exportRecords('cold', props.dateStart, props.dateEnd)"
        >
            <UIcon name="i-lucide-download" class="shrink-0 mt-0.5" />
            <span>Exporter la liste des records de froid</span>
        </ULink>
    </div>
</template>
