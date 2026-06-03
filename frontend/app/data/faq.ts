import type { AccordionItem } from "@nuxt/ui";

export const faqHeroData = {
    title: "FAQ",
    description:
        "Retrouvez ici les réponses aux questions les plus fréquentes sur DataClimat et ses indicateurs.",
};

export const faqItems: AccordionItem[] = [
    {
        label: "Qu'est-ce que DataClimat ?",
        content:
            "DataClimat est un site de visualisation de données climatiques françaises, développé par l'association Data For Good en partenariat avec l'association Infoclimat. Il permet de suivre l'évolution de la température en France à travers plusieurs indicateurs : l'Indicateur Thermique National (ITN), les écarts à la normale et les records de température.",
    },
    {
        label: "D'où proviennent les données ?",
        content:
            "Les données sont issues des mesures open source de Météo-France. Elles couvrent un réseau de stations météorologiques réparties sur l'ensemble du territoire français.",
    },
    {
        label: "À quelle fréquence les données sont-elles mises à jour ?",
        content:
            "Les données sont mises à jour quotidiennement toutes les 10 minutes, au fil des mesures transmises par les stations météorologiques.",
    },
    {
        label: "Qu'est-ce qu'une normale climatique ?",
        content:
            "Une normale climatique est une valeur de référence calculée sur une période de 30 ans. Sur DataClimat, la période de référence utilisée est 1991–2020. Elle sert de base de comparaison pour évaluer si les températures actuelles sont au-dessus ou en-dessous de la moyenne historique.",
    },
    {
        label: "Comment interpréter un écart à la normale positif ?",
        content:
            "Un écart à la normale positif signifie que la température mesurée est supérieure à la moyenne de référence 1991–2020. À l'inverse, un écart négatif indique une température inférieure à cette moyenne. Par exemple, un écart de +2°C signifie qu'il fait 2°C de plus que la normale pour cette période.",
    },
    {
        label: "Qu'est-ce que l'Indicateur Thermique National (ITN) ?",
        content:
            "L'ITN est la température moyenne quotidienne de la France métropolitaine, calculée à partir de 30 stations de référence définies par Météo-France. Ces stations existent depuis au moins 1945 et sont situées en plaine, à l'abri des microclimats locaux, pour garantir une mesure représentative à l'échelle nationale.",
    },
    {
        label: "Pourquoi je ne trouve pas ma station dans la page d'écart de température à la normale ?",
        content: `Pour qu'une station soit éligible au calcul d'un écart à la normale, elle doit remplir deux conditions : avoir au moins 24 années de données sur la période 1991–2020, et avoir une classe de qualité de mesure de température comprise entre 1 et 4 selon la classification de Météo-France: si ces${+" deux critères ne sont pas remplies, la station n'apparait pas dans la page d'écart de température à la normale."}`,
    },
    {
        label: "Pourquoi je ne trouve pas ma station dans la page des records de température ?",
        content: `Pour qu'une station soit éligible à l'établissement d'un record, elle doit remplir deux conditions : avoir au moins 50 années de données de mesure de température, et avoir une classe de qualité de mesure de température comprise entre 1 et 3 selon la classification de Météo-France: si ces${+" deux critères ne sont pas remplies, la station n'apparait pas dans la page des records de température."}`,
    },
    {
        label: "Qu'est-ce qu'un record de température ?",
        content:
            "Un record de température est la valeur la plus extrême (la plus chaude ou la plus froide) jamais mesurée par une station sur une période d'analyse donnée. Pour être prise en compte, la station doit disposer d'au moins 50 années de données et avoir une classe de qualité de mesure en température comprise entre 1 et 3.",
    },
    {
        label: "Quelle est la différence entre un record absolu et un record battu ?",
        content:
            "Un record absolu est la valeur la plus extrême jamais mesurée à ce jour. Un record battu est une valeur qui était un record absolu au moment où elle a été mesurée, mais qui a depuis été dépassée. La liste des records battus retrace l'historique des records successifs d'une station ou d'une région.",
    },
    {
        label: "Comment sont définies les saisons sur DataClimat ?",
        content:
            "DataClimat utilise la définition climatologique des saisons :\n- Printemps : du 1er mars au 31 mai\n- Été : du 1er juin au 31 août\n- Automne : du 1er septembre au 30 novembre\n- Hiver : du 1er décembre au 28 (ou 29) février",
    },
];
