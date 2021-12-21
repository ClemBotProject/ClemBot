import { NuxtAxiosInstance } from '@nuxtjs/axios'
import Public from './routes/Public'
import CustomPrefix from './routes/CustomPrefix'
import WelcomeMessage from './routes/WelcomeMessage'
import Tags from './routes/Tags'
import GuildSettings from './routes/GuildSetting'

export default class ApiClient {
  $axios: NuxtAxiosInstance
  public: Public
  customPrefix: CustomPrefix
  welcomeMessage: WelcomeMessage
  tags: Tags
  guildSettings: GuildSettings

  constructor(axios: NuxtAxiosInstance) {
    this.$axios = axios
    this.public = new Public(axios)
    this.customPrefix = new CustomPrefix(axios)
    this.welcomeMessage = new WelcomeMessage(axios)
    this.tags = new Tags(axios)
    this.guildSettings = new GuildSettings(axios)
  }
}
