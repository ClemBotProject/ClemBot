<template>
  <div>
    <nuxt-link :to="{ path: '/' }">
      <img
        id="main-logo"
        class="mx-3 mt-3"
        src="ClemBotLogo.svg"
        alt="ClemBot"
        width="7%"
      />
    </nuxt-link>
    <b-navbar
      id="splash-card"
      class="is-transparent has-shadow is-fixed-top mb-4"
    >
      <template #start>
        <b-navbar-item
          id="nav"
          class="is-spaced is-tab"
          tag="nuxt-link"
          :to="{ path: '/wiki' }"
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
        <b-navbar-item
          href="https://discord.com/api/oauth2/authorize?client_id=710672266245177365&permissions=1543630070&scope=bot"
        >
          <b-button icon-left="plus" class="is-primary">
            <b>Invite to Server </b>
          </b-button>
        </b-navbar-item>
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
      </template>
    </b-navbar>
    <section class="hero">
      <nuxt />
    </section>
    <Footer />
  </div>
</template>
<style scoped lang="scss">
.section {
  height: 20%;
}

#main-logo {
  position: fixed;
  z-index: 200;
}

#splash-card {
  opacity: 0.95;
}

#discord-login {
  background: #5865f2;
  box-shadow: rgba(0, 0, 0, 0.15) 1.95px 1.95px 2.6px;
  text-decoration: none;
}

#nav {
  left: 38%;
}

#tray-icons {
  transition: all 1.2s ease-in-out;
}

#tray-icons :hover {
  transform: scale(1.1);
  color: white;
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
