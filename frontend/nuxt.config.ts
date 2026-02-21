// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
    // Enable SSR to improve loading time and SEO.
    // For more info: https://nuxt.com/docs/4.x/guide/concepts/rendering#client-side-rendering.
    ssr: true,
    compatibilityDate: "2025-07-15",
    devtools: { enabled: true }, // false for production

    modules: [
        "@nuxt/eslint",
        "@nuxt/test-utils",
        "@nuxt/ui",
        "@nuxt/image",
        "@nuxt/fonts",
        "nuxt-echarts",
    ],

    runtimeConfig: {
        public: {
            apiBase: "", // api url will be injected when the container is launched with an env variable
        },
    },

    css: ["~/assets/css/main.css"],
    ui: {
        colorMode: false,
    },
    fonts: {
        provider: "google",
    },
    app: {
        head: {
            title: "InfoClimat - Dashboard",
            htmlAttrs: {
                lang: "fr",
            },
            link: [{ rel: "icon", type: "image/x-icon", href: "/favicon.ico" }],
        },
    },
    echarts: {
        renderer: ["svg", "canvas"],
        charts: ["BarChart", "LineChart"],
        components: ["DatasetComponent", "GridComponent", "TooltipComponent"],
        features: ["LabelLayout", "UniversalTransition"],
    },
});
