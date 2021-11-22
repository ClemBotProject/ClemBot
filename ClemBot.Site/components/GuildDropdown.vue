<template>
  <b-dropdown class="is-right" mobile-modal scrollable max-height="400">
    <template #trigger>
      <b-button
        icon-left="discord"
        type="has-background-grey-darker has-text-light"
        icon-right="menu-down"
      >
        <b>Select Server</b>
      </b-button>
    </template>
    <div class="divider">Configure</div>
    <div
      v-for="guild in userGuildsConfig"
      :key="guild"
      @mouseenter="guild.isHovered = true"
      @mouseleave="guild.isHovered = false"
    >
      <b-dropdown-item class="py-1">
        <div class="columns is-vcentered">
          <div class="column is-3">
            <b-image
              v-if="!guild.isHovered"
              class="is-32x32"
              rounded
              :src="`https://cdn.discordapp.com/icons/${guild.id}/${guild.icon}.png?size=128`"
            >
            </b-image>
            <b-icon
              class="pl-2 py-1 my-1"
              v-else-if="guild.isHovered && guild.isAdded"
              icon="wrench"
            />
            <b-icon class="pl-2 py-1 my-1" v-else icon="plus" />
          </div>
          <div class="column has-text-justified">
            <b> {{ guild.name }} </b>
          </div>
        </div>
      </b-dropdown-item>
    </div>
    <div class="divider">Add</div>
    <div
      v-for="guild in userGuildsAdd"
      :key="guild"
      @mouseenter="guild.isHovered = true"
      @mouseleave="guild.isHovered = false"
    >
      <b-dropdown-item class="py-1" has-link>
        <a
          :href="`https://discord.com/api/oauth2/authorize?client_id=${$config.discordClientId}&permissions=${$config.oauthPermissions}&scope=bot&guild_id=${guild.id}`"
        >
          <div class="columns is-vcentered" target="_blank">
            <div class="column is-3">
              <b-image
                v-if="!guild.isHovered"
                class="is-32x32"
                rounded
                :src="`https://cdn.discordapp.com/icons/${guild.id}/${guild.icon}.png?size=128`"
              >
              </b-image>
              <b-icon
                class="pl-2 py-1 my-1"
                v-else-if="guild.isHovered && guild.isAdded"
                icon="wrench"
              />
              <b-icon class="pl-2 py-1 my-1" v-else icon="plus" />
            </div>
            <div class="column has-text-justified is-three-quarters">
              <b> {{ guild.name }} </b>
            </div>
          </div>
        </a>
      </b-dropdown-item>
    </div>
  </b-dropdown>
</template>

<script lang="ts">
import Vue from 'vue'
interface Guild {
  id: string
  name: string
  icon: string
  owner: boolean
  permissions: number
  features: string[]
  claims: string[]
  isAdded: boolean
  isHovered: boolean
}

export default Vue.extend({
  data() {
    const userGuildsConfig: Array<Guild> = []
    const userGuildsAdd: Array<Guild> = []
    return {
      userGuildsConfig,
      userGuildsAdd,
    }
  },
  mounted() {
    if (this.$auth.loggedIn && this.$auth.strategy.name === 'local') {
      let userGuilds = (this.$auth.user?.guilds as Array<Guild>)
        .filter(
          // https://discord.com/developers/docs/topics/permissions
          (g) => (g.permissions & 0x8) == 0x8 || (g.permissions & 0x02) == 0x02
        )
        .sort((a, b) => a.name.localeCompare(b.name))
        .map((g) => ({ ...g, isHovered: false }))

      userGuilds.forEach((x) => this.$set(x, 'isHovered', false))

      this.userGuildsConfig = userGuilds.filter((x) => x.isAdded)
      this.userGuildsAdd = userGuilds.filter((x) => !x.isAdded)
    }
  },
})
</script>
