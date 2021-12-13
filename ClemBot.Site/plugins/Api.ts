import { Context, Plugin } from '@nuxt/types'
import { Inject } from '@nuxt/types/app'
import ApiClient from '~/services/api/ApiClient'

declare module '@nuxt/types' {
  interface Context {
    $api: ApiClient
  }
}

declare module 'vue/types/vue' {
  interface Vue {
    $api: ApiClient
  }
}

const api: Plugin = (ctx: Context, inject: Inject) => {
  ctx.$api = new ApiClient(ctx.app.$axios)
  inject('api', ctx.$api)
}

export default api
