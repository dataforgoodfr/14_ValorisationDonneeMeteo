interface TextSection {
    icon: string;
    title: string;
    paragraphs: string[];
}

interface Objective {
    icon: string;
    title: string;
    description: string;
}

export const leProjetHeroData = {
    title: "Le projet collaboratif",
    description:
        "DataClimat est un outil open source de visualisation des données climatologiques françaises, né de la collaboration entre Infoclimat et Data For Good.",
};

export const leProjetGenesis: TextSection = {
    icon: "i-lucide-lightbulb",
    title: "Pourquoi DataClimat ?",
    paragraphs: [
        "Les données météorologiques sont abondantes, mais leur accessibilité reste un défi. Elles sont souvent difficiles à extraire ou à comparer rapidement.",
        "DataClimat est né d'un constat simple : Infoclimat dispose d'une richesse de données historiques exceptionnelle — des décennies de mesures sur des milliers de stations — mais cet donnée climatique restait largement inexploité par ceux qui en auraient le plus besoin : journalistes, prévisionnistes, enseignants, citoyens curieux.",
        "Data For Good a apporté les compétences techniques pour transformer cette matière première en un outil de visualisation moderne, interactif, accessible et ouvert à tous.",
    ],
};

export const leProjetObjectivesSection = {
    icon: "i-lucide-target",
    title: "Ce que l'outil permet",
};

export const leProjetObjectives: Objective[] = [
    {
        icon: "i-lucide-layout-dashboard",
        title: "Un tableau de bord météo en temps réel",
        description:
            "La page d'accueil fonctionne comme un dashboard : records battus aujourd'hui, anomalies en cours, tendance des derniers jours. D'un coup d'œil, vous savez ce qu'il s'est passé récemment et ce qui mérite l'attention.",
    },
    {
        icon: "i-lucide-bar-chart-2",
        title: "Visualiser et comparer",
        description:
            "Des graphiques interactifs permettent de comparer les données dans le temps et dans l'espace, en France Métropolitaine ou à l'échelle locale. Identifier rapidement si une température est exceptionnelle ou parfaitement normale au regard des dernières années.",
    },
    {
        icon: "i-lucide-download",
        title: "Exporter librement",
        description:
            "Chaque graphique et chaque jeu de données est exportable. Journalistes, prévisionnistes, chercheurs : intégrez directement les visuels ou les données brutes dans vos bulletins et publications.",
    },
    {
        icon: "i-lucide-clock",
        title: "Des données mises à jour en continu",
        description:
            "Les mesures sont actualisées toutes les 10 minutes. L'outil reflète l'état actuel du réseau et permet d'ancrer tout commentaire dans des faits récents et vérifiables.",
    },
];

export const leProjetFacts: TextSection = {
    icon: "i-lucide-shield-check",
    title: "Des faits, rien que des faits",
    paragraphs: [
        "DataClimat se concentre exclusivement sur les données du passé et du présent, issues de mesures réelles par des stations météo et mises à disposition par Méteo-France.",
        "L'objectif est de permettre à chacun de contextualiser un événement climatique — une canicule, un hiver doux, une sécheresse — en le comparant aux données historiques. Est-ce que cet été est vraiment le plus chaud jamais enregistré ? Est-ce que ce mois de janvier froid est exceptionnel ou dans la norme des 50 dernières années ? DataClimat répond à ces questions par les chiffres.",
        "Cet ancrage dans le réel est aussi une réponse à la désinformation climatique : en rendant les données historiques accessibles, lisibles et exportables, DataClimat donne à chacun les moyens de construire un discours informé, basé sur les faits mesurés et vérifiables.",
    ],
};

export const leProjetOpenSource: TextSection = {
    icon: "i-lucide-code-2",
    title: "Un outil ouvert",
    paragraphs: [
        "DataClimat est un projet entièrement open source, développé essentiellement par des bénévoles Data For Good et maintenu par Infoclimat.",
        "Les données utilisées proviennent des mesures open data de Météo-France. Elles sont librement réutilisables dans le respect des licences en vigueur.",
    ],
};
