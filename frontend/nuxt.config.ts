// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
    compatibilityDate: "2025-07-15",
    devtools: { enabled: true },
    modules: [
        "@nuxt/eslint",
        "@nuxt/test-utils",
        "@nuxt/ui",
        "@nuxt/image",
        "@nuxt/fonts",
        "nuxt-echarts",
    ],
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
    runtimeConfig: {
        public: {
            apiBase: "",
        },
    },
});
