import { Module, VuexModule, Mutation } from 'vuex-module-decorators'

interface OauthGuild {
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
class OauthUser extends VuexModule {
  guilds: Array<OauthGuild> = []

  @Mutation
  set(guilds: Array<OauthGuild>) {
    this.guilds = guilds
  }

  get guildsWithAddPerms() {
    return this.guilds
  }
}
