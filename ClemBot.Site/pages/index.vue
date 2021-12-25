<template>
  <div>
    <section id="splash-image" class="hero has-shadow is-fullheight">
      <div class="hero-body is-vcentered">
        <div id="hero-columns" class="columns is-desktop">
          <div class="column is-two-fifths">
            <img
              id="main-logo"
              class="
                mx-6
                mt-6
                is-justify-content-center is-align-content-center
              "
              src="ClemBotLogo.svg"
              alt="ClemBot"
            />
          </div>
          <div
            id="splash-card"
            class="card column has-background-black-ter mt-6 mr-6"
          >
            <div class="card-content">
              <h1 class="is-size-1 title has-text-white">ClemBot</h1>
              <p class="subtitle has-text-white">
                The modular and configurable open source Discord Bot for all
                your needs
              </p>
            </div>
            <div class="tile is-ancestor">
              <div class="tile is-vertical is-6">
                <div id="nav-tile" class="tile is-parent">
                  <a
                    href="https://discord.com/api/oauth2/authorize?client_id=710672266245177365&permissions=398828104950&scope=bot"
                  >
                    <article
                      id="nav-child"
                      class="
                        add-to-discord
                        tile
                        is-child
                        notification
                        is-primary
                        column
                      "
                    >
                      <div class="columns is-mobile">
                        <p class="title column has-text-centered mt-3">
                          Summon me to your Server!
                        </p>
                        <b-icon
                          class="column is-one-quarter mt-3"
                          icon="discord"
                          custom-size="mdi-48px"
                        />
                      </div>
                    </article>
                  </a>
                </div>
                <div id="nav-tile" class="tile is-parent has-shadow">
                  <article
                    id="nav-child"
                    class="
                      tile
                      is-child
                      notification
                      has-background-black has-shadow
                      py-5
                    "
                  >
                    <p class="title">Stats</p>
                    Currently running <b>{{ guildsCount }}</b> Servers and
                    watching <b>{{ usersCount }} </b> Users
                    <br />
                    <br />
                    Over <b>{{ commandsCount }}</b> commands handled!
                  </article>
                </div>
              </div>
              <div id="nav-tile" class="tile is-parent is-vertical">
                <nuxt-link :to="{ path: '/wiki/intro' }">
                  <article
                    id="nav-child"
                    class="tile is-child notification is-primary"
                  >
                    <p class="title">Feature Packed</p>
                    <div class="content subtitle">
                      <ul>
                        <li><b>Moderation</b></li>
                        <ul>
                          <li>Banning</li>
                          <li>Muting</li>
                          <li>Warning</li>
                        </ul>
                        <li><b>Custom Prefixes</b></li>
                        <li><b>User and Message Logging</b></li>
                        <li><b>Role Management</b></li>
                        <li><b>Welcome Messages</b></li>
                        <li><b>Custom Tags</b></li>
                      </ul>
                    </div>
                  </article>
                </nuxt-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
    <section class="hero is-fullheight-with-navbar">
      <div class="hero-body">
        <div class="tile is-ancestor is-vertical">
          <div v-for="chunk in features" :key="chunk">
            <div class="tile is-ancestor">
              <div v-for="feature in chunk" :key="feature">
                <feature-card
                  :title="feature.title"
                  :description="feature.description"
                  :image="feature.image"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'
import { chunkArray } from '~/services/Utilities'
import FeatureCard from '~/components/FeatureCard.vue'

export default Vue.extend({
  components: { FeatureCard },
  middleware: 'HomeAuthCheck',
  data() {
    return {
      guildsCount: 'Unknown',
      usersCount: 'Unknown',
      commandsCount: 'Unknown',

      features: chunkArray(
        [
          {
            title: 'Message Logging',
            description:
              'Complete message edit and deletion logging to make moderating easy.',
            image: 'FeatureImages/MessageEdit.png',
          },
          {
            title: 'Moderation',
            description:
              'Ban troublesome members, mute spammers, and keep track of warnings to provide some accountability in your community.',
            image: 'FeatureImages/MemberMute.png',
          },
          {
            title: 'User Logging',
            description:
              "Keep track of your servers' joins and leaves with welcome messages and logging posts.",
            image: 'FeatureImages/UserJoinEmbed.png',
          },
          {
            title: 'Custom Tags',
            description:
              'Create custom tags and invoke them later to easily convey repeated information or just an inside joke.',
            image: 'FeatureImages/TagInvoke.png',
          },
          {
            title: 'Assignable Roles',
            description:
              'Set roles as assignable, and allow your members to self assign what roles they want.',
            image: 'FeatureImages/AssignRoles.png',
          },
          {
            title: 'Custom Prefixes',
            description:
              "Do you have multiple bots in your server? Clembot's command prefix is completely customizable!",
            image: 'FeatureImages/CustomPrefix.png',
          },
        ],
        3
      ),
    }
  },

  async fetch() {
    const stats = await this.$api.public.getGlobalStats()

    if (stats === null) {
      console.log('Getting public guild stats failed')
      return
    }

    this.guildsCount = stats.guilds ?? 'many'
    this.usersCount = stats.users ?? 'all the'
    this.commandsCount = stats.commands ?? 'tons of'
  },
})
</script>

<style scoped>
.add-to-discord {
  background: #5865f2;
  box-shadow: rgba(0, 0, 0, 0.15) 1.95px 1.95px 2.6px;
  text-decoration: none;
}

#splash-card {
  opacity: 0.9;
}

#splash-image {
  box-shadow: rgba(0, 0, 0, 0.35) 0px 5px 15px;
  background-image: url('static/SplashBkg.svg');
  background-repeat: no-repeat;
  transform: translatez(0);
  -webkit-transform: translatez(0);
  user-select: none;
  background-position: bottom;
}

#help-tiles {
  border-radius: 25px;
}

#nav-tile {
  -webkit-transition: all 0.1s ease-in-out;
  -moz-transition: all 0.1s ease-in-out;
  -ms-transition: all 0.1s ease-in-out;
  -o-transition: all 0.1s ease-in-out;
  transition: all 0.1s ease-in-out;
}

#nav-tile :hover {
  -webkit-transition: all 0.1s ease-in-out;
  -moz-transition: all 0.1s ease-in-out;
  -o-transition: all 0.1s ease-in-out;
  transition: all 0.1s ease-in-out;
  -ms-transform: scale(1.015, 1.015);
  /* IE 9 */
  -webkit-transform: scale(1.015, 1.015);
  /* Safari */
  transform: scale(1.015, 1.015);
}

#nav-child :hover {
  transition: none;
  transform: none;
}

#hero-columns {
  width: 100%;
}

@media (max-width: 1024px) {
  #hero-columns {
    padding-right: 0;
  }

  #splash-card {
    margin: 1.5rem !important;
  }
}
</style>
