<template>
  <section class="section is-medium" id="wiki">
    <div class="columns">
      <div class="column is-2">
        <b-menu id="wiki-menu">
          <b-menu-list label="ClemBot Wiki">
            <nuxt-link :to="{ path: '/wiki/Intro' }">
              <b-menu-item label="Intro" class="pb-1"></b-menu-item>
            </nuxt-link>
            <nuxt-link :to="{ path: '/wiki/CustomPrefix' }">
              <b-menu-item label="Custom Prefix" class="pb-1"></b-menu-item>
            </nuxt-link>
            <nuxt-link :to="{ path: '/wiki/Claims' }">
              <b-menu-item label="Claims" class="pb-1"></b-menu-item>
            </nuxt-link>
            <b-menu-item :active="moderationActive" expanded>
              <template #label="props">
                Moderation
                <b-icon
                  class="is-pulled-right"
                  :icon="props.expanded ? 'menu-down' : 'menu-up'"
                ></b-icon>
              </template>
              <b-menu-item
                tag="router-link"
                :to="{ path: '/wiki/moderation/Overview' }"
                class="pb-1"
                label="Overview"
              ></b-menu-item>
              <nuxt-link :to="{ path: '/wiki/moderation/Warn' }">
                <b-menu-item class="pb-1" label="Warn"></b-menu-item>
              </nuxt-link>
              <nuxt-link :to="{ path: '/wiki/moderation/Mute' }">
                <b-menu-item class="pb-1" label="Mute"></b-menu-item>
              </nuxt-link>
              <nuxt-link :to="{ path: '/wiki/moderation/Ban' }">
                <b-menu-item class="pb-1" label="Ban"></b-menu-item>
              </nuxt-link>
            </b-menu-item>
            <nuxt-link :to="{ path: '/wiki/DesignatedChannels' }">
              <b-menu-item
                label="Designated Channels"
                class="pb-1"
              ></b-menu-item>
            </nuxt-link>
            <nuxt-link :to="{ path: '/wiki/AssignableRoles' }">
              <b-menu-item label="Assignable Roles" class="pb-1"></b-menu-item>
            </nuxt-link>
            <nuxt-link :to="{ path: '/wiki/Tags' }">
              <b-menu-item label="Tags" class="pb-1"></b-menu-item>
            </nuxt-link>
            <nuxt-link :to="{ path: '/wiki/WelcomeMessage' }">
              <b-menu-item label="Welcome Messages" class="pb-1"></b-menu-item>
            </nuxt-link>
          </b-menu-list>
        </b-menu>
      </div>
      <div id="wiki-component" class="column has-background-black-ter">
        <nuxt-child />
      </div>
    </div>
  </section>
</template>

<script lang="ts">
import Vue from 'vue'

export default Vue.extend({
  data() {
    return {
      moderationActive: true,
    }
  },
})
</script>

<style scoped>
#wiki-component {
  border-radius: 15px;
  box-shadow: rgba(0, 0, 0, 0.35) 0px 5px 15px;
  overflow-y: auto;
}

#wiki {
  margin-top: 4rem;
}
</style>
