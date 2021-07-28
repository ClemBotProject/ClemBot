const isProd = () => process.env.PROD === '1'
const prodUrl = 'http://clembot.site:80/api'
const devUrl = 'http://localhost:5001/api'

export default {
  // Disable server-side rendering: https://go.nuxtjs.dev/ssr-mode
  ssr: false,

  // Global page headers: https://go.nuxtjs.dev/config-head
  head: {
    title: 'ClemBot',
    htmlAttrs: {
      lang: 'en',
    },
    meta: [
      { charset: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      { hid: 'description', name: 'description', content: '' },
    ],
    link: [{ rel: 'icon', type: 'image/x-icon', href: '/ClemBotLogo.svg' }],
  },

  axios: {
    baseURL: isProd() ? prodUrl : devUrl, // Used as fallback if no runtime config is provided
  },

  // Global CSS: https://go.nuxtjs.dev/config-css
  css: ['assets/css/main.scss'],

  env: {
    prod: process.env.PROD === '1',
    baseUrl: process.env.BASE_URL,
  },

  // Plugins to run before rendering page: https://go.nuxtjs.dev/config-plugins
  plugins: [
    '@/plugins/api.ts', // our plugin
  ],

  // Auto import components: https://go.nuxtjs.dev/config-components
  components: true,

  // Modules for dev and build (recommended): https://go.nuxtjs.dev/config-modules
  buildModules: [
    // https://go.nuxtjs.dev/typescript
    '@nuxt/typescript-build',
  ],

  // Modules: https://go.nuxtjs.dev/config-modules
  modules: [
    '@nuxtjs/axios',

    // https://go.nuxtjs.dev/buefy
    ['nuxt-buefy', { css: false }],
  ],

  // Build Configuration: https://go.nuxtjs.dev/config-build
  build: {
    extend(config, { isClient }) {
      // Extend only webpack config for client-bundle
      if (isClient) {
        config.devtool = 'source-map'
      }
    },
  },
}
