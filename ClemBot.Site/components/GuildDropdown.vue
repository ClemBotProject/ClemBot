<template>
  <b-dropdown
    v-model="activeGuild"
    :class="side"
    mobile-modal
    scrollable
    max-height="400"
  >
    <template v-if="activeGuild === null" #trigger>
      <b-button
        icon-left="discord"
        type="has-background-grey-darker has-text-light"
        icon-right="menu-down"
      >
        <b>Select Server</b>
      </b-button>
    </template>
    <template v-else #trigger>
      <b-button
        type="has-background-grey-darker has-text-light"
        icon-right="menu-down"
      >
        <div class="columns is-vcentered">
          <div v-if="showicon" class="column is-3">
            <b-image
              class="is-32x32"
              rounded
              :src="`https://cdn.discordapp.com/icons/${activeGuild.id}/${activeGuild.icon}.png?size=128`"
            >
            </b-image>
          </div>
          <div class="column">
            <b> {{ activeGuild.name }} </b>
          </div>
        </div>
      </b-button>
    </template>
    <div class="divider">Configure</div>
    <div
      v-for="guild in userGuildsConfig"
      :key="guild.id"
      @mouseenter="guild.isHovered = true"
      @mouseleave="guild.isHovered = false"
    >
      <b-dropdown-item :value="guild" class="py-1">
        <nuxt-link :to="{ path: `/dashboard/${guild.id}/guild` }">
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
        </nuxt-link>
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
import { Guild } from 'services/Models/Guild'

export default Vue.extend({
  props: {
    side: String,
    showicon: {
      type: Boolean,
      default: true,
    },
  },
  data() {
    const userGuildsConfig: Array<Guild> = []
    const userGuildsAdd: Array<Guild> = []
    let activeGuild: Guild | null = null
    return {
      userGuildsConfig,
      userGuildsAdd,
      activeGuild,
    }
  },
  mounted() {
    if (this.$auth.loggedIn && this.$auth.strategy.name === 'local') {
      let userGuilds = (this.$auth.user?.guilds as Array<Guild>)
        .slice()
        .sort((a, b) => a.name.localeCompare(b.name))
        .map((g) => ({ ...g, isHovered: false } as Guild))

      userGuilds.forEach((x) => this.$set(x, 'isHovered', false))

      this.userGuildsConfig = userGuilds.filter((x) => x.isAdded)
      this.userGuildsAdd = userGuilds.filter(
        (x) =>
          !x.isAdded &&
          ((x.permissions & 0x8) == 0x8 || (x.permissions & 0x02) == 0x02)
      )

      if (this.$route.params.id !== undefined) {
        //@ts-ignore this fails the type checker for some reason but it works fine
        this.activeGuild =
          this.userGuildsConfig.find((x) => x.id === this.$route.params.id) ??
          null
      }
    }
  },
})
</script>
