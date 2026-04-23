<script setup lang="ts">
import Section from "../Section.vue";
import ITNCard from "./ITNCard.vue";
</script>
<template>
    <div>
        <Section :title="'LES INFORMATIONS À RETENIR'">
            <div class="flex flex-col gap-5 md:flex-row">
                <ITNCard />
                <ITNCard />
                <ITNCard />
            </div>
        </Section>
    </div>
</template>
