import { NuxtAxiosInstance } from '@nuxtjs/axios'
import Public from './routes/public'

export default class ApiClient {
  $axios: NuxtAxiosInstance
  public: Public

  constructor(axios: NuxtAxiosInstance) {
    this.$axios = axios
    this.public = new Public(axios)
  }
}
