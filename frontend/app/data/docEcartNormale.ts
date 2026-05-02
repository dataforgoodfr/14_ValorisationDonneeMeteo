import type { InfoSection } from "~/types/common";

export const ecartNormaleHeroData = {
    title: "Écart à la normale",
    description:
        "L'écart de température à la normale est définit comme la différence de la température moyenne sur une période donnée et la température moyenne de référence calculée sur la période 1991–2020 pour une durée équivalente",
};

export const ecartNormaleSections: InfoSection[] = [
    {
        label: "Définition",
        content:
            "Les normales climatiques correspondent à des valeurs statistiques calculées" +
            " sur une période de référence de 30 ans. Celles-ci servent de point de comparaison" +
            " pour analyser le climat actuel et le changement climatique." +
            "\n(https://meteofrance.com/, https://fr.wikipedia.org/wiki/Normale_climatique)" +
            "\n\nSur le site dataclimat.fr la période des normales considérées est la période de référence 1991-2020" +
            "\nL'écart de température à la normale est alors la différence entre la température" +
            " moyenne mesurée et la température moyenne entre 1991 et 2020 (période des normales)",
    },
    {
        label: "Méthode de calcul",
        content: [
            {
                title: "Écart à la normale quotidien en France métropolitaine",
                text:
                    "L'écart de température à la normale en France métropolitaine calculé chaque jour" +
                    " est la différence entre la valeur de l'Indicateur Thermique National (ITN) mesurée ce jour" +
                    " et la valeur de l'ITN moyennée, pour ce même jour de l'année, entre 1991 et 2020 (période des normales) ",
            },
            {
                title: "Écart à la normale quotidien d'une station",
                text:
                    "L'écart de température à la normale d'une station calculé chaque jour" +
                    " est la différence entre la température moyenne TNTXM de la station mesurée ce jour" +
                    " et la valeur de la température moyenne TNTXM de la station moyennée sur 30 ans ce" +
                    " même jour de l'année",
            },
            {
                title: "Écart à la normale mensuel/annuel ",
                text:
                    "Les normales mensuelles/annuelles sont calculées en moyennant les normales" +
                    " quotidiennes pour chaque mois/année",
            },
        ],
    },
    {
        label: "Stations éligibles",
        content:
            "Le calcul des normales ne peut s'effectuer que si le nombre de données manquantes n'est pas" +
            " supérieur à celui préconisé par la norme OMM (https://donneespubliques.meteofrance.fr/client/document/normales-methode_299.pdf)" +
            "\n\nAinsi, pour qu'une station soit éligible au calcul d'un écart à la normale et apparaisse sur le site dataclimat.fr," +
            " cette station doit avoir au moins 24 ans de données entre 1991-2020 (période des normales) et avoir une classe de qualité" +
            " de mesure de température définie par MéteoFrance entre 1 et 4.",
    },
    {
        label: "Sources",
        content:
            "- Les données sont issues de mesures open source de Météo-France" +
            "\n- Informations sur les normales climatiques: https://donneespubliques.meteofrance.fr/client/document/normales-methode_299.pdf)" +
            " https://meteofrance.com/, https://fr.wikipedia.org/wiki/Normale_climatique)" +
            "\n- Classe des stations: https://www.data.gouv.fr/datasets/fiches-dinformations-sur-les-stations",
    },
];
