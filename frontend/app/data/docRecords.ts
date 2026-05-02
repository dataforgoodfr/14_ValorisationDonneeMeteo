import type { InfoSection } from "~/types/common";

export const recordsHeroData = {
    title: "Records",
    description:
        "Les records de température correspondent aux valeurs extrêmes — maximales ou minimales — mesurées depuis la création d'une station disposant d'au moins 50 ans de données.",
};

export const recordsSections: InfoSection[] = [
    {
        label: "Définition",
        content:
            "Une mesure de température est un record si c'est la valeur la plus extrême" +
            " (chaude ou froide) jamais mesurée, à date, sur la période d'analyse sélectionnée.",
    },
    {
        label: "Méthode de calcul",
        content: [
            {
                title: "Records absolus",
                text:
                    "Un records absolu est la (et l'unique) valeur de température la plus extrême jamais" +
                    " mesurée sur la période d'analyse sélectionnée",
            },
            {
                title: "Records battus",
                text:
                    "Les records battus sont la liste des records qu'une station ou une région a connu" +
                    " au cours du temps, après 50 années de mesures. Chaque record battu fut un record absolu" +
                    " à sa date du record, mais il existe plusieurs records battus qui ne sont plus des records" +
                    " absolus: le record absolu d'une station ou d'une région est, en fait, le dernier record battu." +
                    "\nPour chaque station qui a plus de 50 années de données, le premier record battu de la liste est" +
                    " défini comme le record absolu des 50 premières années de mesures.",
            },
            {
                title: "Période d'analyse",
                text:
                    "La période d'analyse permet d'afficher les records mensuels ou saisonniers (absolus ou battus) pour une" +
                    " partie de l'année (un mois ou un saison) seulement:" +
                    "\n- si la période d'analyse est un mois, les records mensuels, du mois sélectionné, sont affichés." +
                    "\n- si la période d'analyse est une saison, les records saisonniers, de la saison sélectionnée, sont affichés." +
                    "\n- si la période est 'Année complète' les records annuels (tous mois confondus) sont affichés.",
            },
        ],
    },
    {
        label: "Stations éligibles",
        content:
            "Pour être pertinent un record ne peut être déclaré comme tel que si la station a au moins 50 annnées de données et si" +
            " sa classe de qualité de mesure de température définie par Météo-France est comprise entre 1 et 3.",
    },
    {
        label: "Sources",
        content:
            "- Les données sont issues de mesures open source de Météo-France" +
            "\n- Classe des stations: https://www.data.gouv.fr/datasets/fiches-dinformations-sur-les-stations",
    },
    {
        label: "Nota Bene",
        content:
            "La définition des saisons utilisées est la définition climatologique:" +
            "\n- Printemps: du 1er mars au 31 mai" +
            "\n- Été: du 1er juin au 31 août" +
            "\n- Automne: du 1er septembre au 30 novembre" +
            "\n- Hiver: du 1er décembre au 28 (ou 29) février",
    },
];
