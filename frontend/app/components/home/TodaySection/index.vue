<script setup lang="ts">
import Section from "../Section.vue";

const today = new Date();
</script>
<template>
    <div>
        <Section :title="`AUJOURD'HUI - ${formatDateLongForDisplay(today)}`">
            <p class="text-sm text-gray-600">
                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed
                euismod, nunc ut laoreet tincidunt, nunc nisl aliquam nunc, eget
                aliquam nisl nunc euismod nunc.
            </p>
        </Section>
    </div>
</template>
<style lang="css" scoped>
.red {
    color: #ff6467;
}
.blue {
    color: #82c4e8;
}
</style>
