import { NuxtAxiosInstance } from '@nuxtjs/axios'

interface Prefix {
  prefixes: Array<string>
}

export default class CustomPrefix {
  $axios: NuxtAxiosInstance

  constructor(axios: NuxtAxiosInstance) {
    this.$axios = axios
  }

  async getCustomPrefix(id: string): Promise<string> {
    const prefixes = await this.$axios.$get<Prefix>(
      `guilds/${id}/customprefixes`
    )
    return prefixes.prefixes[0]
  }

  async setCustomPrefix(id: string, prefix: string): Promise<boolean> {
    await this.$axios.$post<number>('customprefixes/add', {
      guildId: id,
      prefix: prefix,
    })
    return true
  }
}
