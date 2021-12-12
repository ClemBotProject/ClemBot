import { NuxtAxiosInstance } from '@nuxtjs/axios'

export interface Tag {
    name: string
    content: string
    creationDate: string
    useCount: string
}

interface Model {
    tags: Array<Tag>
}

export default class Tags{
  $axios: NuxtAxiosInstance

  constructor(axios: NuxtAxiosInstance) {
    this.$axios = axios
  }

  async getGuildTags(id: string): Promise<Array<Tag>> {
    let resp = await this.$axios.$get<Model>(`guilds/${id}/tags`)
    return resp.tags
  }
}
