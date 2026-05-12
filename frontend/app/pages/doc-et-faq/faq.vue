<script setup lang="ts">
import PagesHero from "~/components/layout/PagesHero.vue";
import { faqHeroData, faqItems } from "~/data/faq";
</script>

<template>
    <UContainer class="flex flex-col gap-y-16">
        <PagesHero
            :title="faqHeroData.title"
            :description="faqHeroData.description"
        />

        <UAccordion type="multiple" collapsible :items="faqItems">
            <template #body="{ item }">
                <p class="whitespace-pre-wrap text-sm text-muted pb-4 px-1">
                    {{ item.content }}
                </p>
            </template>
        </UAccordion>
    </UContainer>
</template>
