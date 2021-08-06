import { Module, VuexModule, Mutation } from 'vuex-module-decorators'

interface oauthGuild {
  id: string
  name: string
  icon: string
  owner: boolean
  permissions: number
}

@Module({
  name: 'mymodule',
  stateFactory: true,
  namespaced: true,
})
// eslint-disable-next-line @typescript-eslint/no-unused-vars
class oauthGuilds extends VuexModule {
  guilds: Array<oauthGuild> = []

  @Mutation
  set(guilds: Array<oauthGuild>) {
    this.guilds = guilds
  }

  get guildsWithAddPerms() {
    return this.guilds
  }
}
