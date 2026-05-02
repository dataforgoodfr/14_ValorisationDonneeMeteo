<script setup lang="ts">
import PagesHero from "~/components/layout/PagesHero.vue";

const heroData = {
    title: "FAQ",
    description:
        "Retrouvez ici les réponses aux questions les plus fréquentes sur DataClimat et ses indicateurs.",
};

const faqItems = [
    {
        label: "Qu'est-ce que DataClimat ?",
        value: "0",
        content:
            "DataClimat est un site de visualisation de données climatiques françaises, développé par l'association Infoclimat en partenariat avec Data for Good. Il permet de suivre l'évolution de la température en France à travers plusieurs indicateurs : l'Indicateur Thermique National (ITN), les écarts à la normale et les records de température.",
    },
    {
        label: "D'où proviennent les données ?",
        value: "1",
        content:
            "Les données sont issues des mesures open source de MétéoFrance. Elles couvrent un réseau de stations météorologiques réparties sur l'ensemble du territoire français.",
    },
    {
        label: "À quelle fréquence les données sont-elles mises à jour ?",
        value: "2",
        content:
            "Les données sont mises à jour quotidiennement toutes les 10 minutes, au fil des mesures transmises par les stations météorologiques.",
    },
    {
        label: "Qu'est-ce qu'une normale climatique ?",
        value: "3",
        content:
            "Une normale climatique est une valeur de référence calculée sur une période de 30 ans. Sur DataClimat, la période de référence utilisée est 1991–2020. Elle sert de base de comparaison pour évaluer si les températures actuelles sont au-dessus ou en dessous de la moyenne historique.",
    },
    {
        label: "Comment interpréter un écart à la normale positif ?",
        value: "4",
        content:
            "Un écart à la normale positif signifie que la température mesurée est supérieure à la moyenne de référence 1991–2020. À l'inverse, un écart négatif indique une température inférieure à cette moyenne. Par exemple, un écart de +2°C signifie qu'il fait 2°C de plus que la normale pour cette période.",
    },
    {
        label: "Qu'est-ce que l'Indicateur Thermique National (ITN) ?",
        value: "5",
        content:
            "L'ITN est la température moyenne quotidienne de la France métropolitaine, calculée à partir de 30 stations de référence définies par MétéoFrance. Ces stations existent depuis au moins 1945 et sont situées en plaine, à l'abri des microclimats locaux, pour garantir une mesure représentative à l'échelle nationale.",
    },
    {
        label: "Pourquoi certaines stations ne disposent-elles pas de normale calculée ?",
        value: "6",
        content:
            "Pour qu'une station soit éligible au calcul d'un écart à la normale, elle doit remplir deux conditions : avoir au moins 24 années de données sur la période 1991–2020, et avoir une classe de qualité de mesure de température comprise entre 1 et 4 selon la classification de MétéoFrance.",
    },
    {
        label: "Qu'est-ce qu'un record de température ?",
        value: "7",
        content:
            "Un record de température est la valeur la plus extrême (la plus chaude ou la plus froide) jamais mesurée à une station sur une période d'analyse donnée. Pour être pris en compte, la station doit disposer d'au moins 50 années de données et avoir une classe de qualité comprise entre 1 et 3.",
    },
    {
        label: "Quelle est la différence entre un record absolu et un record battu ?",
        value: "8",
        content:
            "Un record absolu est la valeur la plus extrême jamais mesurée à ce jour. Un record battu est une valeur qui était un record absolu au moment où elle a été mesurée, mais qui a depuis été dépassée. La liste des records battus retrace l'historique des records successifs d'une station ou d'une région.",
    },
    {
        label: "Comment sont définies les saisons sur DataClimat ?",
        value: "9",
        content:
            "DataClimat utilise la définition climatologique des saisons :\n- Printemps : du 1er mars au 31 mai\n- Été : du 1er juin au 31 août\n- Automne : du 1er septembre au 30 novembre\n- Hiver : du 1er décembre au 28 (ou 29) février",
    },
];
</script>

<template>
    <UContainer class="flex flex-col gap-y-16">
        <PagesHero
            :title="heroData.title"
            :description="heroData.description"
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
