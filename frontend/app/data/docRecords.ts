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
            " (chaude ou froide) jamais mesurée, à date, depuis la création de la station.",
    },
    {
        label: "Méthode de calcul",
        content: [
            {
                title: "Records absolus",
                text:
                    "Un record absolu est la (et l'unique) valeur de température la plus extrême jamais" +
                    " mesurée depuis la création de la station",
            },
            {
                title: "Records battus",
                text:
                    "Les records battus sont la liste des records qu'une station ou une région a connu" +
                    " au cours du temps, après 50 années de mesures. Chaque record battu fut un record absolu" +
                    " à sa date du record, mais il existe plusieurs records battus qui ne sont plus des records" +
                    " absolus: le record absolu d'une station ou d'une région est, en fait, le dernier record battu." +
                    "\nUne station qui n'a pas battu de records après ses 50 permières années de mesure n'a donc, par définition," +
                    " aucun record battu listé.",
            },
            {
                title: "Types de records",
                text:
                    "Trois types de records sont disponibles sur DataClimat: records annuels, saisonniers ou mensuels." +
                    "\n- Un record annuel est une valeur qui est la plus extrême tous mois confondus." +
                    "\n- Un record saisonnier est une valeur qui est la plus extrême en ne considérant que la saison sélectionnée: " +
                    " il est possible d'afficher les records saisonniers de toutes les saisons ou d'une saison en particulier." +
                    "\n- Un record mensuel est une valeur qui est la plus extrême en ne considérant que le mois sélectionné: " +
                    " il est possible d'afficher les records mensuels de tous les mois ou d'un mois en en particulier.",
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
