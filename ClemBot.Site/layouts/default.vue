<template>
  <div>
    <nuxt-link :to="{ path: '/' }">
      <img
        id="main-logo"
        class="mx-3 mt-3"
        src="/ClemBotLogo.svg"
        alt="ClemBot"
        width="7%"
      />
    </nuxt-link>
    <b-navbar id="splash-card" transparent shadow class="is-fixed-top mb-4">
      <template #start>
        <b-navbar-item
          id="nav"
          class="is-spaced is-tab"
          target="_blank"
          href="https://docs.clembot.io"
        >
          <b-icon icon="script" class="mr-1" size="is-small" /><b> Wiki </b>
        </b-navbar-item>
        <b-navbar-item
          id="nav"
          class="is-spaced is-tab"
          tag="nuxt-link"
          :to="{ path: '/status' }"
        >
          <b-icon icon="heart-cog-outline" class="mr-1" size="is-small" />
          <b>Status</b>
        </b-navbar-item>
        <b-navbar-item
          id="nav"
          class="is-spaced is-tab"
          tag="nuxt-link"
          :to="{ path: '/support' }"
        >
          <b-icon icon="patreon" class="mr-1" size="is-small" />
          <b>Support</b>
        </b-navbar-item>
      </template>
      <template #end>
        <div id="socials">
          <b-navbar-item v-if="!$auth.loggedIn">
            <b-button @click="login" icon-left="login" class="is-primary">
              <b>Login With Discord</b>
            </b-button>
          </b-navbar-item>
          <GuildDropdown v-else side="is-right" />
          <UserDisplay v-if="$auth.loggedIn" class="ml-3 mr-1" />
          <b-navbar-item target="_blank" href="https://discord.gg/mhrVuyh">
            <b-icon id="tray-icons" icon="discord"> </b-icon>
          </b-navbar-item>
          <b-navbar-item
            id="tray-icons"
            target="_blank"
            href="https://github.com/ClemBotProject/ClemBot"
          >
            <b-icon icon="github"> </b-icon>
          </b-navbar-item>
        </div>
      </template>
    </b-navbar>
    <section class="hero">
      <nuxt v-if="!$slots.default" />
      <slot />
    </section>
    <Footer />
  </div>
</template>

<script lang="ts">
import Vue from 'vue'

export default Vue.extend({
  methods: {
    async login() {
      await this.$auth.loginWith('discord')
    },
  },
})
</script>

<style scoped lang="scss">
.section {
  height: 20%;
}

#main-logo {
  position: fixed;
  z-index: 200;
  min-width: 5rem;
  max-width: 6rem;
}

#discord-login {
  background: #5865f2;
  box-shadow: rgba(0, 0, 0, 0.15) 1.95px 1.95px 2.6px;
  text-decoration: none;
}

#nav {
  left: 38%;
}

#splash-card {
  opacity: 0.95;
}

#tray-icons {
  transition: all 1.2s ease-in-out;
}

#tray-icons :hover {
  transform: scale(1.1);
  color: white;
}

#socials {
  display: flex;
  align-items: center;
  justify-content: center;
}

#discord-login :hover + .animation-wrapper {
  animation-name: ckw;
  animation-duration: 1.5s;
  /* Things added */
  animation-iteration-count: infinite;
  display: inline-block;
  /* <--- */
}
@keyframes ckw {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
