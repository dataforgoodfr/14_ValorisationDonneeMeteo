<script setup lang="ts">
import Section from '../Section.vue';

const {
    yesterday,
} = useHomeData();

const yesterdayLess365Days = computed(() => {
    const date = new Date();
    date.setDate(date.getDate() - 365);
    return date;
});


</script>

<template>
    <div>
        <Section :title="`CES 365 DERNIERS JOURS -  ${formatDateLongForDisplay(yesterdayLess365Days)} au ${formatDateLongForDisplay(yesterday)}`">
            <p class="text-sm text-gray-600">
                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed
                euismod, nunc ut laoreet tincidunt, nunc nisl aliquam nunc, eget
                aliquam nisl nunc euismod nunc.
            </p>
          </Section>
    </div>
</template>