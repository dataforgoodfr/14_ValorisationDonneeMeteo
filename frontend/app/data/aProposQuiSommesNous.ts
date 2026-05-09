interface AssociationSection {
    logo: string;
    logoAlt: string;
    title: string;
    paragraphs: string[];
    firstParagraphLink?: {
        text: string;
        href: string;
        label: string;
        before: string;
        after: string;
    };
}

export const quiSommesNousHeroData = {
    title: "Qui sommes nous ?",
    description:
        "DataClimat est né de la rencontre entre deux associations engagées : Infoclimat et Data For Good.",
};

export const infoclimatSection: AssociationSection = {
    logo: "/images/logo-infoclimat.png",
    logoAlt: "Infoclimat",
    title: "Infoclimat",
    firstParagraphLink: {
        before: "Fondée en 2002 par des passionnés de météorologie, ",
        label: "Infoclimat",
        href: "https://asso.infoclimat.fr/",
        text: "Infoclimat",
        after: " est aujourd'hui l'un des plus grands réseaux météorologiques amateurs de France. L'association fédère plusieurs milliers de stations météo bénévoles réparties sur l'ensemble du territoire, des plaines aux sommets alpins, en passant par les territoires ultramarins.",
    },
    paragraphs: [
        "Grâce à cet engagement bénévole, Infoclimat collecte, contrôle et diffuse en open data des observations météorologiques continues, constituant une base de données d'une richesse exceptionnelle. Ces données, accumulées sur plusieurs décennies, forment le socle factuel sur lequel s'appuie DataClimat.",
        "Au-delà du réseau de mesure, l'association porte des valeurs fortes : partage de la connaissance, accessibilité des données scientifiques et indépendance vis-à-vis des intérêts commerciaux. Rejoindre l'association, c'est contribuer à la pérennité de cette mission d'intérêt général.",
    ],
};

export const dataforgoodSection: AssociationSection = {
    logo: "/images/logo-dataforgood.png",
    logoAlt: "Data For Good",
    title: "Data For Good",
    paragraphs: [
        "Créée en 2014, Data For Good est une association qui mobilise des bénévoles aux compétences numériques — data scientists, ingénieurs logiciel, designers, développeurs — pour les mettre au service de projets d'intérêt général portés par des associations, ONG ou organismes publics.",
        "L'association fonctionne par « saisons » : des sprints de quelques mois durant lesquels des équipes bénévoles s'investissent sur des projets concrets, de la phase de cadrage jusqu'à la livraison d'un outil ou d'une analyse. Chaque saison réunit des dizaines de volontaires autour de causes variées : santé, environnement, éducation, solidarité...",
        "Data For Good croit que la technologie et les données peuvent être des leviers puissants pour le bien commun, à condition d'être pilotées par des valeurs et non par la seule logique de profit. DataClimat est l'un des projets nés de cette conviction.",
    ],
};
