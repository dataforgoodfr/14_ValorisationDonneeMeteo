<script setup lang="ts">
import PagesHero from "~/components/layout/PagesHero.vue";
import {
    leProjetHeroData,
    leProjetGenesis,
    leProjetObjectivesSection,
    leProjetObjectives,
    leProjetFacts,
    leProjetOpenSource,
} from "~/data/aProposLeProjet";
</script>

<template>
    <UContainer class="flex flex-col gap-y-16">
        <PagesHero
            :title="leProjetHeroData.title"
            :description="leProjetHeroData.description"
        />

        <!-- Genèse du projet -->
        <div class="flex flex-col gap-6">
            <div class="flex items-center gap-3">
                <UIcon :name="leProjetGenesis.icon" class="size-6 shrink-0" />
                <h2 class="text-xl font-semibold">
                    {{ leProjetGenesis.title }}
                </h2>
            </div>
            <div class="flex flex-col gap-4 text-sm text-muted">
                <p v-for="p in leProjetGenesis.paragraphs" :key="p">{{ p }}</p>
            </div>
        </div>

        <UDivider />

        <!-- Ce que l'outil permet -->
        <div class="flex flex-col gap-8">
            <div class="flex items-center gap-3">
                <UIcon
                    :name="leProjetObjectivesSection.icon"
                    class="size-6 shrink-0"
                />
                <h2 class="text-xl font-semibold">
                    {{ leProjetObjectivesSection.title }}
                </h2>
            </div>
            <div class="flex flex-col gap-8">
                <div
                    v-for="obj in leProjetObjectives"
                    :key="obj.title"
                    class="flex gap-4 border-l-2 border-primary pl-5"
                >
                    <UIcon
                        :name="obj.icon"
                        class="size-5 shrink-0 text-primary mt-0.5"
                    />
                    <div class="flex flex-col gap-1.5">
                        <h3 class="font-semibold">{{ obj.title }}</h3>
                        <p class="text-sm text-muted">{{ obj.description }}</p>
                    </div>
                </div>
            </div>
        </div>

        <UDivider />

        <!-- Des faits, rien que des faits -->
        <div class="flex flex-col gap-6">
            <div class="flex items-center gap-3">
                <UIcon :name="leProjetFacts.icon" class="size-6 shrink-0" />
                <h2 class="text-xl font-semibold">{{ leProjetFacts.title }}</h2>
            </div>
            <div class="flex flex-col gap-4 text-sm text-muted">
                <p v-for="p in leProjetFacts.paragraphs" :key="p">{{ p }}</p>
            </div>
        </div>

        <UDivider />

        <!-- Un outil ouvert -->
        <div class="flex flex-col gap-6 pb-8">
            <div class="flex items-center gap-3">
                <UIcon
                    :name="leProjetOpenSource.icon"
                    class="size-6 shrink-0"
                />
                <h2 class="text-xl font-semibold">
                    {{ leProjetOpenSource.title }}
                </h2>
            </div>
            <div class="flex flex-col gap-4 text-sm text-muted">
                <p v-for="p in leProjetOpenSource.paragraphs" :key="p">
                    {{ p }}
                </p>
            </div>
        </div>
    </UContainer>
</template>
