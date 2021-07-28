<template>
  <section class="section is-medium">
    <div class="columns">
      <div class="column is-2">
        <b-menu id="wiki-menu">
          <b-menu-list label="ClemBot Wiki">
            <b-menu-item
              label="Intro"
              class="pb-1"
              @click="changeWikiPage('wiki/Intro')"
            ></b-menu-item>
            <b-menu-item
              label="Custom Prefix"
              class="pb-1"
              @click="changeWikiPage('wiki/CustomPrefix')"
            ></b-menu-item>
            <b-menu-item
              label="Claims"
              class="pb-1"
              @click="changeWikiPage('wiki/Claims')"
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
                class="pb-1"
                label="Overview"
                @click="changeWikiPage('wiki/moderation/Overview')"
              ></b-menu-item>
              <b-menu-item
                class="pb-1"
                label="Warn"
                @click="changeWikiPage('wiki/moderation/Warn')"
              ></b-menu-item>
              <b-menu-item
                class="pb-1"
                label="Mute"
                @click="changeWikiPage('wiki/moderation/Mute')"
              ></b-menu-item>
              <b-menu-item
                class="pb-1"
                label="Ban"
                @click="changeWikiPage('wiki/moderation/Ban')"
              ></b-menu-item>
            </b-menu-item>
            <b-menu-item
              label="Designated Channels"
              class="pb-1"
              @click="changeWikiPage('wiki/DesignatedChannels')"
            ></b-menu-item>
            <b-menu-item
              label="Assignable Roles"
              class="pb-1"
              @click="changeWikiPage('wiki/AssignableRoles')"
            ></b-menu-item>
            <b-menu-item
              label="Tags"
              class="pb-1"
              @click="changeWikiPage('wiki/Tags')"
            ></b-menu-item>
            <b-menu-item
              label="Welcome Messages"
              class="pb-1"
              @click="changeWikiPage('wiki/WelcomeMessage')"
            ></b-menu-item>
          </b-menu-list>
        </b-menu>
      </div>
      <div id="wiki-component" class="column has-background-black-ter">
        <component :is="activeItem"></component>
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
      activeItem: () => import('~/components/wiki/Intro.vue'),
    }
  },
  methods: {
    changeWikiPage(path: string) {
      this.activeItem = () => import(`~/components/${path}.vue`)
      window.scrollTo(0, 0)
    },
  },
})
</script>

<style scoped>
#wiki-component {
  border-radius: 15px;
  box-shadow: rgba(0, 0, 0, 0.35) 0px 5px 15px;
  overflow-y: auto;
}
</style>
