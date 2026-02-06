// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  ssr: true, //false : use client-side only rendering to generate .output/public/index.html
  compatibilityDate: "2025-07-15",
  devtools: { enabled: false }, // false for production
  // couche de compilation runtime genere un index static pour  nginx
  nitro: {
  preset: 'node-server'
   },

  modules: ["@nuxt/test-utils", "@nuxt/ui", "@nuxt/image", '@nuxt/fonts'],
  css: ['~/assets/css/main.css'],
  ui: {
    colorMode: false
  },
  app: {
    head: {
      title: 'InfoClimat - Dashboard',
      htmlAttrs: {
        lang: 'fr',
      },
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' },
      ],
    },
  },
   
});
