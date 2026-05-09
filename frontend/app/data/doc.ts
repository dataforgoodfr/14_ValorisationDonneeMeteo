import { itnHeroData, itnSections } from "~/data/docItn";
import {
    ecartNormaleHeroData,
    ecartNormaleSections,
} from "~/data/docEcartNormale";
import { recordsHeroData, recordsSections } from "~/data/docRecords";
import type { InfoSection } from "~/types/common";

export interface DocEntry {
    title: string;
    description: string;
    sections: InfoSection[];
    icon: string;
    to: string;
}

export const docHeroData = {
    title: "Documentation",
    description:
        "Retrouvez ici la documentation détaillée des métriques et indicateurs disponibles sur DataClimat : définitions, méthodes de calcul et sources.",
};

export const docEntries: DocEntry[] = [
    {
        ...itnHeroData,
        sections: itnSections,
        icon: "i-lucide-thermometer-sun",
        to: "/temperature/itn",
    },
    {
        ...ecartNormaleHeroData,
        sections: ecartNormaleSections,
        icon: "i-lucide-move-horizontal",
        to: "/temperature/ecart-normale",
    },
    {
        ...recordsHeroData,
        sections: recordsSections,
        icon: "i-lucide-sun-snow",
        to: "/temperature/records",
    },
];
