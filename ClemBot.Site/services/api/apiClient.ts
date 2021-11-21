import { NuxtAxiosInstance } from '@nuxtjs/axios'
import Public from './routes/Public'

export default class ApiClient {
  $axios: NuxtAxiosInstance
  public: Public

  constructor(axios: NuxtAxiosInstance) {
    this.$axios = axios
    this.public = new Public(axios)
  }
}
