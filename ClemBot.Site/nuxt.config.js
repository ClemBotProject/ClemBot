// eslint-disable-next-line eqeqeq
const isProd = () => process.env.PROD == '1'
const prodHost = '0.0.0.0'
const localHost = 'localhost'
const prodUrl = 'https://clembot.io:443/api'
const devUrl = 'https://localhost:5001/api'

const runtimeUrl = isProd() ? prodUrl : devUrl

// eslint-disable-next-line no-console
console.log(process.env.DISCORD_CLIENT_ID)

export default {
  // Disable server-side rendering: https://go.nuxtjs.dev/ssr-mode
  //ssr: false,

  server: {
    port: 3000, // default: 3000
    host: isProd() ? prodHost : localHost, // default: localhost
  },

  publicRuntimeConfig: {
    discordClientId: process.env.DISCORD_CLIENT_ID,
    oauthPermissions: process.env.OAUTH_PERMISSIONS,
    defaultPrefix: process.env.DEFAULT_PREFIX
  },
  privateRuntimeConfig: {
    discordClientSecret: process.env.DISCORD_CLIENT_SECRET,
  },

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

  auth: {
    strategies: {
      local: {
        endpoints: {
          login: {
            url: '/authorize/login',
            method: 'post',
            propertyName: 'bearer',
          },
          user: {
            url: '/authorize/user',
            method: 'get',
            propertyName: 'user',
          },
          logout: false,
        },
        tokenRequired: true,
        tokenType: 'Bearer',
      },
      discord: {
        clientId: process.env.DISCORD_CLIENT_ID,
        clientSecret: process.env.DISCORD_CLIENT_SECRET,
        codeChallengeMethod: '',
        scope: ['identify', 'guilds'],
        grantType: 'authorization_code',
      },
    },
  },

  // Global CSS: https://go.nuxtjs.dev/config-css
  css: ['@/assets/css/main.scss'],

  // Plugins to run before rendering page: https://go.nuxtjs.dev/config-plugins
  plugins: [
    '@/plugins/Axios',
    '@/plugins/Api.ts', // our plugin
  ],

  // Auto import components: https://go.nuxtjs.dev/config-components
  components:  [
    '~/components',
    { path: '~/components/support', extensions: ['vue'] },
    { path: '~/components/dashboard', extensions: ['vue'] }
  ],

  // Modules for dev and build (recommended): https://go.nuxtjs.dev/config-modules
  buildModules: [
    // https://go.nuxtjs.dev/typescript
    '@nuxt/typescript-build',
    '@nuxtjs/dotenv',
  ],

  // Modules: https://go.nuxtjs.dev/config-modules
  modules: [
    '@nuxtjs/axios',
    '@nuxtjs/auth-next',

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
