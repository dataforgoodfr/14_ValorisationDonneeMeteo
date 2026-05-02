import type { InfoSection } from "~/types/common";

export const itnHeroData = {
    title: "Indicateur Thermique National",
    description:
        "L'Indicateur Thermique National (ITN) est la température moyenne mesurée à l'échelle du pays (moyenne des températures minimales et maximales sur 30 stations météorologiques réparties de manière équilibrée en France).",
};

export const itnSections: InfoSection[] = [
    {
        label: "Définition",
        content:
            "L'Indicateur Thermique National (ITN) permet de mesurer l'évolution de la" +
            " température moyenne en France métropolitaine. L'ITN est calculé à partir" +
            " des données de 30 stations définies par Météo-France qui existent depuis au" +
            " moins 1945 et qui sont considérées comme suffisamment fiables. Ces stations" +
            " sont réparties dans des zones de plaines et à l'abri des microclimats locaux" +
            " qui pourraient biaiser la valeur de cet indicateur national.",
    },
    {
        label: "Méthode de calcul",
        content: [
            {
                title: "ITN quotidien",
                text:
                    "Chaque jour et dans chaque station, la température minimale Tn" +
                    " (mesurée entre 18h UTC la veille et 18h UTC le jour même) et la" +
                    " température maximale Tx (mesurée entre 6h UTC le jour même et 6h UTC" +
                    " le lendemain) sont relevées. La moyenne de Tn et Tx donne la" +
                    " température moyenne quotidienne (TNTXM). \n" +
                    "L'ITN quotidien est alors la moyenne des TNTXM des 30 stations sélectionnées.",
            },
            {
                title: "ITN mensuel/annuel ",
                text: "L'ITN mensuel/annuel est la moyenne arithmétique des ITN quotidiens sur la période considérée",
            },
        ],
    },
    {
        label: "Stations utilisées",
        content:
            "La liste des 30 stations à considérer pour assurer un calcul pertinent et" +
            " robuste pour analyser l'évolution de l'indicateur sur plusieurs décennies" +
            " a été définie par Météo-France." +
            "\nCette liste et la répartition géographique des stations est disponible sur" +
            " la page dataclimat.fr/itn",
    },
    {
        label: "Sources",
        content:
            "Les données sont issues de mesures open source de Météo-France",
    },
    {
        label: "Nota Bene",
        content:
            "L'une des 30 stations de référence, celle de Reims, a dû changer entre 2012" +
            " et 2014 suite à la fermeture de la base aérienne 112 Reims-Champagne." +
            "\nL'ancienne station de Reims-Courcy a cessé ses mesures en 2014 tandis que la nouvelle station" +
            " de Reims-Prunay a commencé ses relevés en 2012. Ces deux stations ont été en service" +
            " simultanément du 08/05/2012 jusqu'au 24/04/2014, soit durant une période de 717 jours." +
            "\nAprès étude statistique des relevés de ces 2 stations, il apparaît que la température" +
            " TNTXM de la nouvelle station est en moyenne 0,29°C inférieure à celle de l'ancienne" +
            " station. Rapportée à la moyenne des 30 stations de référence, cette différence est" +
            " inférieure à 0,01°C, ce qui est négligeable par rapport à la précision de ±0,1°C de la" +
            " mesure de l'ITN.\nIl a donc été décidé, pour le calcul de l'ITN, concernant la station" +
            " de Reims, d'utiliser la station de Reims-Courcy (code 51183001) jusqu'au 07/05/2012" +
            " inclus, puis celle de Reims-Prunay (code 51449002) à partir du 08/05/2012.",
    },
];
