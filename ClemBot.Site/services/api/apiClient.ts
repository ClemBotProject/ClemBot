import { NuxtAxiosInstance } from '@nuxtjs/axios'
import Public from './routes/Public'
import CustomPrefix from './routes/CustomPrefix'
import WelcomeMessage from './routes/WelcomeMessage'

export default class ApiClient {
  $axios: NuxtAxiosInstance
  public: Public
  customPrefix: CustomPrefix
  welcomeMessage: WelcomeMessage

  constructor(axios: NuxtAxiosInstance) {
    this.$axios = axios
    this.public = new Public(axios)
    this.customPrefix = new CustomPrefix(axios)
    this.welcomeMessage = new WelcomeMessage(axios)
  }
}
