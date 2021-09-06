<template>
  <b-dropdown class="is-right" mobile-modal scrollable max-height="400">
    <template #trigger>
      <b-button icon-left="discord" type="is-primary" icon-right="menu-down">
        <b>Select Server</b>
      </b-button>
    </template>
    <div
      v-for="guild in userGuilds
        .filter(
          // https://discord.com/developers/docs/topics/permissions
          (g) => (g.permissions & 0x8) == 0x8 || (g.permissions & 0x02) == 0x02
        )
        .sort((a, b) => a.name.localeCompare(b.name))"
      :key="guild"
    >
      <b-dropdown-item>
        <div class="columns is-vcentered">
          <div class="column is-2">
            <b-image
              class="is-32x32"
              rounded
              :src="`https://cdn.discordapp.com/icons/${guild.id}/${guild.icon}.png?size=128`"
            >
            </b-image>
          </div>
          <div class="column is-vcentered">
            <b> {{ guild.name }} </b>
          </div>
        </div>
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
  // eslint-disable-next-line camelcase
  permissions_new: string
}

export default Vue.extend({
  data() {
    const userGuilds: Array<Guild> = []
    return {
      userGuilds,
    }
  },
  async fetch() {
    if (this.$auth.loggedIn && this.$auth.strategy.name === 'discord') {
      this.userGuilds = await fetch('https:/discord.com/api/users/@me/guilds', {
        // @ts-ignore
        headers: { Authorization: this.$auth.strategy.token.get() },
      }).then((resp) => resp.json())
    }
  },
})
</script>
