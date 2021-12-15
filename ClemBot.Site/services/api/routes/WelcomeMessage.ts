import { github } from '@nuxtjs/auth-next'
import { NuxtAxiosInstance } from '@nuxtjs/axios'

interface WelcomeMessage{
  message: string
}

export default class CustomPrefix {
  $axios: NuxtAxiosInstance

  constructor(axios: NuxtAxiosInstance) {
    this.$axios = axios
  }

  async getWelcomeMessage(id: string): Promise<string> {
    let foo = await this.$axios.$get<WelcomeMessage>(`guilds/${id}/getWelcomeMessage`)
    return foo.message
  }

  async setWelcomeMessage(id: string, message: string): Promise<boolean> {
    await this.$axios.$post<number>(`guilds/${id}/SetWelcomeMessage`, {
        Message: message,
    })
    return true
  }
}
