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
        "Grâce à cet engagement bénévole, Infoclimat collecte, contrôle et diffuse en open data des observations météorologiques continues, constituant une base de données d'une richesse exceptionnelle.",
        "Au-delà du réseau de mesure, l'association porte des valeurs fortes : partage de la connaissance, accessibilité des données scientifiques et indépendance vis-à-vis des intérêts commerciaux. Rejoindre l'association, c'est contribuer à la pérennité de cette mission d'intérêt général.",
    ],
};

export const dataforgoodSection: AssociationSection = {
    logo: "/images/logo-dataforgood.png",
    logoAlt: "Data For Good",
    title: "Data For Good",
    paragraphs: [
        "Créée en 2014, Data For Good est une association qui mobilise plus de 8000 bénévoles avec des compétences liées à l'analyse de données — data scientists, ingénieurs, designers, développeurs — pour les mettre au service de projets d'intérêt général portés par des associations, ONG ou organismes publics.",
        "Les projets Data For Good réunissent des dizaines de bénévoles autour de causes variées - santé, environnement, éducation, solidarité ... - dans le but de créer et livrer un outil, un plaidoyer ou un site web à l'association afin qu'elle puisse l'utiliser et le faire évoluer si besoin.",
        "Data For Good croit que la technologie et les données peuvent être des leviers puissants pour le bien commun, tout en luttant contre les schémas de pensée qui l'ont engendré : DataClimat est l'un des projets nés de cette conviction.",
    ],
};
