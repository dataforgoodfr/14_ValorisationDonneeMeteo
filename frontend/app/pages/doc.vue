<script setup lang="ts">
import PagesHero from "~/components/layout/PagesHero.vue";
import { itnHeroData, itnSections } from "~/data/docItn";
import {
    ecartNormaleHeroData,
    ecartNormaleSections,
} from "~/data/docEcartNormale";
import { recordsHeroData, recordsSections } from "~/data/docRecords";
import type { InfoSection } from "~/types/common";

const heroData = {
    title: "Documentation",
    description:
        "Retrouvez ici la documentation détaillée des métriques et indicateurs disponibles sur DataClimat : définitions, méthodes de calcul et sources.",
};

const docs = [
    {
        ...itnHeroData,
        sections: itnSections,
        icon: "i-lucide-thermometer-sun",
        to: "/itn",
    },
    {
        ...ecartNormaleHeroData,
        sections: ecartNormaleSections,
        icon: "i-lucide-move-horizontal",
        to: "/ecart-normale",
    },
    {
        ...recordsHeroData,
        sections: recordsSections,
        icon: "i-lucide-sun-snow",
        to: "/records",
    },
];

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
            :title="heroData.title"
            :description="heroData.description"
        />

        <div class="flex flex-col gap-12">
            <div
                v-for="doc in docs"
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
