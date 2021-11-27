import { github } from '@nuxtjs/auth-next'
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
      `guilds/customprefixes?guildId=${id}`
    )
    return prefixes.prefixes[0]
  }
}