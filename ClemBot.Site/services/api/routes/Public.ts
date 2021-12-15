import { NuxtAxiosInstance } from '@nuxtjs/axios'

interface GlobalStats {
  guilds: string
  users: string
  commands: string
}

export default class Public {
  $axios: NuxtAxiosInstance

  constructor(axios: NuxtAxiosInstance) {
    this.$axios = axios
  }

  async getGlobalStats(): Promise<GlobalStats | null> {
    let stats;
    try {
      stats = await this.$axios.$get<GlobalStats>('public/globalstats')
    }
    catch(e) {
      console.log(e)
    }
    
    return stats ?? null
  }
}
