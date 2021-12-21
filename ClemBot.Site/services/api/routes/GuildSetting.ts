import { NuxtAxiosInstance } from '@nuxtjs/axios'
import { GuildSettings } from '~/services/GuildSettings'

interface Setting {
    setting: GuildSettings
}

export default class GuildSetting {
  $axios: NuxtAxiosInstance

  constructor(axios: NuxtAxiosInstance) {
    this.$axios = axios
  }

  async getCanEmbedLink(id: string): Promise<boolean> {
    const setting = await this.$axios.$get<Setting & {value: boolean}>(
      `guildsettings/${id}/${GuildSettings.allowEmbedLinks}`
    )

    return setting.value
  }

  async setCanEmbedLink(id: string, val: boolean): Promise<boolean> {
    let resp = await this.$axios.$post<{status: boolean}>(`guildsettings/${id}/${GuildSettings.allowEmbedLinks}?value=${val}`)
    return resp.status
  }
}