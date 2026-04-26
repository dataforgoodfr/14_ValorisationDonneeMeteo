<script setup lang="ts">
interface InternalNavLink {
    label: string;
    to: string;
}

interface ExternalNavLink {
    label: string;
    href: string;
}

interface SocialLink {
    icon: string;
    href: string;
    label: string;
}

const navLinks: InternalNavLink[] = [
    { label: "Le Projet", to: "/" },
    { label: "Le Dashboard", to: "/" },
    { label: "Écart de température à la normale", to: "/ecart-normale" },
    { label: "Indicateur Thermique National", to: "/itn" },
    { label: "Records de température", to: "/records" },
    { label: "Min & Max de température", to: "/min-max" },
];

const infoclimatLinks: ExternalNavLink[] = [
    { label: "infoclimat.fr", href: "https://www.infoclimat.fr/" },
    { label: "Le site de l'association", href: "https://asso.infoclimat.fr/" },
    {
        label: "Devenir adhérent",
        href: "https://asso.infoclimat.fr/infos/formulaire.php",
    },
    { label: "Faire un don", href: "https://asso.infoclimat.fr/" },
];

const infoclimatSocials: SocialLink[] = [
    {
        icon: "i-lucide-instagram",
        href: "https://www.instagram.com/infoclimat/",
        label: "Instagram",
    },
    {
        icon: "i-lucide-linkedin",
        href: "https://www.linkedin.com/company/association-infoclimat/",
        label: "LinkedIn",
    },
];

const dataForGoodLinks: ExternalNavLink[] = [
    { label: "Le site de l'association", href: "https://dataforgood.fr/" },
    {
        label: "Devenir bénévole",
        href: "https://authentik.services.dataforgood.fr/if/flow/main-page-enrollment/?next=%2F",
    },
    { label: "Faire un don", href: "https://dataforgood.fr/faire-un-don" },
];

const dataForGoodSocials: SocialLink[] = [
    {
        icon: "i-lucide-youtube",
        href: "https://www.youtube.com/channel/UCA_utdbmVhAOFujulWlaaCQ",
        label: "YouTube",
    },
    {
        icon: "i-lucide-linkedin",
        href: "https://www.linkedin.com/company/dataforgood/",
        label: "LinkedIn",
    },
    {
        icon: "i-simple-icons-bluesky",
        href: "https://bsky.app/profile/dataforgood.fr",
        label: "Bluesky",
    },
];
</script>

<template>
    <footer class="bg-[#12161F] border-t border-dark-700 mt-8">
        <UContainer>
            <div class="grid grid-cols-1 gap-10 py-8 sm:grid-cols-3 lg:gap-16">
                <div class="flex flex-col gap-5">
                    <div class="flex items-center gap-2">
                        <UIcon
                            name="i-lucide-hexagon"
                            class="size-6 text-primary"
                        />
                        <span
                            class="font-title font-medium text-base text-dark-200"
                        >
                            DataClimat
                        </span>
                    </div>
                    <ul class="space-y-2.5">
                        <li v-for="link in navLinks" :key="link.label">
                            <NuxtLink
                                :to="link.to"
                                class="text-sm text-dark-400 hover:text-dark-200 transition-colors"
                            >
                                {{ link.label }}
                            </NuxtLink>
                        </li>
                    </ul>
                </div>

                <div class="flex flex-col gap-5">
                    <div class="flex items-center gap-2">
                        <img
                            src="/images/logo-infoclimat.png"
                            alt="Infoclimat"
                            class="h-7 w-auto"
                        />
                        <span class="font-medium text-base text-dark-200">
                            Infoclimat
                        </span>
                    </div>
                    <ul class="space-y-2.5">
                        <li v-for="link in infoclimatLinks" :key="link.label">
                            <a
                                :href="link.href"
                                target="_blank"
                                rel="noopener noreferrer"
                                class="text-sm text-dark-400 hover:text-dark-200 transition-colors"
                            >
                                {{ link.label }}
                            </a>
                        </li>
                    </ul>
                    <div class="flex items-center gap-3">
                        <a
                            v-for="social in infoclimatSocials"
                            :key="social.label"
                            :href="social.href"
                            target="_blank"
                            rel="noopener noreferrer"
                            :aria-label="social.label"
                            class="text-dark-400 hover:text-dark-200 transition-colors"
                        >
                            <UIcon :name="social.icon" class="size-5" />
                        </a>
                    </div>
                </div>

                <div class="flex flex-col gap-5">
                    <div class="flex items-center gap-2">
                        <img
                            src="/images/logo-dataforgood.png"
                            alt="DataForGood"
                            class="h-7 w-auto"
                        />
                        <span class="font-medium text-base text-dark-200">
                            DataForGood
                        </span>
                    </div>
                    <ul class="space-y-2.5">
                        <li v-for="link in dataForGoodLinks" :key="link.label">
                            <a
                                :href="link.href"
                                target="_blank"
                                rel="noopener noreferrer"
                                class="text-sm text-dark-400 hover:text-dark-200 transition-colors"
                            >
                                {{ link.label }}
                            </a>
                        </li>
                    </ul>
                    <div class="flex items-center gap-3">
                        <a
                            v-for="social in dataForGoodSocials"
                            :key="social.label"
                            :href="social.href"
                            target="_blank"
                            rel="noopener noreferrer"
                            :aria-label="social.label"
                            class="text-dark-400 hover:text-dark-200 transition-colors"
                        >
                            <UIcon :name="social.icon" class="size-5" />
                        </a>
                    </div>
                </div>
            </div>

            <div class="border-t border-dark-700 py-4">
                <p class="text-sm text-dark-400">
                    Tous droits réservés - &copy;
                    {{ new Date().getFullYear() }} Infoclimat et Data for Good
                </p>
            </div>
        </UContainer>
    </footer>
</template>
