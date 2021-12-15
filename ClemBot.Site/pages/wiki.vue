<template>
  <section class="section is-medium" id="wiki">
    <div class="columns">
      <div class="column is-2">
        <b-menu id="wiki-menu">
          <b-menu-list label="ClemBot Wiki">
            <b-menu-item
              tag="router-link"
              :to="{ path: '/wiki/intro' }"
              label="Intro"
              class="pb-1"
            ></b-menu-item>
            <b-menu-item
              tag="router-link"
              :to="{ path: '/wiki/customprefix' }"
              class="pb-1"
              label="Custom Prefix"
            ></b-menu-item>
            <b-menu-item
              tag="router-link"
              :to="{ path: '/wiki/claims' }"
              class="pb-1"
              label="Claims"
            ></b-menu-item>
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
                :to="{ path: '/wiki/moderation/overview' }"
                class="pb-1"
                label="Overview"
              ></b-menu-item>
              <b-menu-item
                tag="router-link"
                :to="{ path: '/wiki/moderation/warn' }"
                class="pb-1"
                label="overview"
              ></b-menu-item>
              <b-menu-item
                tag="router-link"
                :to="{ path: '/wiki/moderation/mute' }"
                class="pb-1"
                label="Mute"
              ></b-menu-item>
              <b-menu-item
                tag="router-link"
                :to="{ path: '/wiki/moderation/ban' }"
                class="pb-1"
                label="Ban"
              ></b-menu-item>
            </b-menu-item>
            <b-menu-item
              tag="router-link"
              :to="{ path: '/wiki/designatedchannels' }"
              class="pb-1"
              label="Designated Channels"
            ></b-menu-item>
            <b-menu-item
              tag="router-link"
              :to="{ path: '/wiki/assignableroles' }"
              class="pb-1"
              label="Assignable Roles"
            ></b-menu-item>
            <b-menu-item
              tag="router-link"
              :to="{ path: '/wiki/tags' }"
              class="pb-1"
              label="Tags"
            ></b-menu-item>
            <b-menu-item
              tag="router-link"
              :to="{ path: '/wiki/welcomemessage' }"
              class="pb-1"
              label="Welcome Message"
            ></b-menu-item>
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
