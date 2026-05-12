<script setup lang="ts">
import PagesHero from "~/components/layout/PagesHero.vue";
import {
    quiSommesNousHeroData,
    infoclimatSection,
    dataforgoodSection,
} from "~/data/aProposQuiSommesNous";
</script>

<template>
    <UContainer class="flex flex-col gap-y-16">
        <PagesHero
            :title="quiSommesNousHeroData.title"
            :description="quiSommesNousHeroData.description"
        />

        <div class="flex flex-col gap-16">
            <!-- Infoclimat -->
            <div class="flex flex-col gap-6">
                <div class="flex items-center gap-3">
                    <img
                        :src="infoclimatSection.logo"
                        :alt="infoclimatSection.logoAlt"
                        class="h-7 w-auto"
                    />
                    <h2 class="text-xl font-semibold">
                        {{ infoclimatSection.title }}
                    </h2>
                </div>

                <div class="flex flex-col gap-4 text-sm text-muted">
                    <p v-if="infoclimatSection.firstParagraphLink">
                        {{ infoclimatSection.firstParagraphLink.before
                        }}<ULink
                            :to="infoclimatSection.firstParagraphLink.href"
                            target="_blank"
                            class="text-primary underline underline-offset-2"
                            >{{
                                infoclimatSection.firstParagraphLink.label
                            }}</ULink
                        >{{ infoclimatSection.firstParagraphLink.after }}
                    </p>
                    <p v-for="p in infoclimatSection.paragraphs" :key="p">
                        {{ p }}
                    </p>
                </div>

                <div class="flex flex-wrap gap-3 mt-2">
                    <UButton
                        to="https://www.infoclimat.fr"
                        target="_blank"
                        variant="outline"
                        trailing-icon="i-lucide-external-link"
                        size="sm"
                    >
                        Visiter infoclimat.fr
                    </UButton>
                    <UButton
                        to="https://asso.infoclimat.fr/infos/formulaire.php"
                        target="_blank"
                        variant="outline"
                        trailing-icon="i-lucide-heart"
                        size="sm"
                    >
                        Adhérer à l'association
                    </UButton>
                </div>
            </div>

            <UDivider />

            <!-- Data For Good -->
            <div class="flex flex-col gap-6">
                <div class="flex items-center gap-3">
                    <img
                        :src="dataforgoodSection.logo"
                        :alt="dataforgoodSection.logoAlt"
                        class="h-7 w-auto"
                    />
                    <h2 class="text-xl font-semibold">
                        {{ dataforgoodSection.title }}
                    </h2>
                </div>

                <div class="flex flex-col gap-4 text-sm text-muted">
                    <p v-for="p in dataforgoodSection.paragraphs" :key="p">
                        {{ p }}
                    </p>
                </div>

                <div class="flex flex-wrap gap-3 mt-2">
                    <UButton
                        to="https://dataforgood.fr"
                        target="_blank"
                        variant="outline"
                        trailing-icon="i-lucide-external-link"
                        size="sm"
                    >
                        Visiter dataforgood.fr
                    </UButton>
                    <UButton
                        to="https://authentik.services.dataforgood.fr/if/flow/main-page-enrollment/?next=%2F"
                        target="_blank"
                        variant="outline"
                        trailing-icon="i-lucide-hand-heart"
                        size="sm"
                    >
                        Devenir bénévole
                    </UButton>
                </div>
            </div>
        </div>
    </UContainer>
</template>
