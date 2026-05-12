<script setup lang="ts">
import PagesHero from "~/components/layout/PagesHero.vue";
import { docHeroData, docEntries } from "~/data/doc";
import type { InfoSection } from "~/types/common";

function toAccordionItems(sections: InfoSection[]) {
    return sections.map((section, i) => ({
        label: section.label,
        value: String(i),
        section,
    }));
}
</script>

<template>
    <UContainer class="flex flex-col gap-y-16">
        <PagesHero
            :title="docHeroData.title"
            :description="docHeroData.description"
        />

        <div class="flex flex-col gap-12">
            <div
                v-for="doc in docEntries"
                :key="doc.title"
                class="flex flex-col gap-4"
            >
                <div class="flex flex-wrap items-center gap-3">
                    <UIcon :name="doc.icon" class="size-5 shrink-0" />
                    <h2 class="text-xl font-semibold">{{ doc.title }}</h2>
                    <UButton
                        :to="doc.to"
                        variant="link"
                        size="sm"
                        trailing-icon="i-lucide-arrow-right"
                        class="ml-auto"
                    >
                        Voir la page
                    </UButton>
                </div>
                <p class="text-sm text-muted">{{ doc.description }}</p>
                <UAccordion
                    type="multiple"
                    collapsible
                    :items="toAccordionItems(doc.sections)"
                >
                    <template #body="{ item }">
                        <div
                            v-if="Array.isArray(item.section.content)"
                            class="flex flex-col gap-3 text-sm pb-4 px-1"
                        >
                            <div
                                v-for="para in item.section.content"
                                :key="para.text"
                                class="flex flex-col gap-1"
                            >
                                <p v-if="para.title" class="font-semibold">
                                    {{ para.title }}
                                </p>
                                <p class="whitespace-pre-wrap text-muted">
                                    {{ para.text }}
                                </p>
                            </div>
                        </div>
                        <p
                            v-else
                            class="whitespace-pre-wrap text-sm text-muted pb-4 px-1"
                        >
                            {{ item.section.content }}
                        </p>
                    </template>
                </UAccordion>
            </div>
        </div>
    </UContainer>
</template>
