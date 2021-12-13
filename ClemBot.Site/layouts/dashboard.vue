<template>
  <div class="sidebar-page">
    <section class="sidebar-layout">
      <b-sidebar :fullheight="true" position="static" open type="is-dark" />
      <b-sidebar :fullheight="true" open type="is-dark">
        <nuxt-link :to="{ path: '/' }">
          <img class="px-6 py-3" src="/ClemBotLogo.svg" alt="ClemBot" />
        </nuxt-link>
        <div class="box mx-3 my-3 has-background-darkest">
          <b-menu class="is-custom-mobile mx-4">
            <div class="is-vcentered"></div>
            <b-menu-list label="Dashboard">
              <b-menu-item
                icon="cog"
                label="Guild"
                tag="nuxt-link"
                to="guild"
              ></b-menu-item>
              <b-menu-item
                icon="book"
                label="Tags"
                tag="nuxt-link"
                to="tags"
              ></b-menu-item>
            </b-menu-list>
          </b-menu>
        </div>
      </b-sidebar>
      <div class="column">
        <section class="hero">
          <div class="hero-body"></div>
        </section>
        <nuxt />
      </div>
    </section>
    <b-navbar id="dashboard-navbar" transparent class="is-fixed-top mb-4">
      <template #end>
        <div id="socials" class="box mx-3 my-3 has-background-dark has-shadow">
          <GuildDropdown side="is-right" />
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
  </div>
</template>

<script>
import Vue from 'vue'
import DefaultLayout from '~/layouts/default.vue'
import { titleCase } from '@/services/Utilities'

export default Vue.extend({
  components: {
    DefaultLayout,
  },
  middleware: 'DashboardAuthCheck',
})
</script>

<style lang="scss">
#socials {
  display: flex;
  align-items: center;
  justify-content: center;
}

#dashboard-navbar {
  background: transparent;
}

.p-1 {
  padding: 1em;
}
.sidebar-page {
  display: flex;
  flex-direction: column;
  width: 100%;
  min-height: 100%;
  // min-height: 100vh;
  .sidebar-layout {
    display: flex;
    flex-direction: row;
    min-height: 100%;
    // min-height: 100vh;
  }
}
@media screen and (max-width: 1023px) {
  .b-sidebar {
    .sidebar-content {
      &.is-mini-mobile {
        &:not(.is-mini-expand),
        &.is-mini-expand:not(:hover):not(.is-mini-delayed) {
          .menu-list {
            li {
              a {
                span:nth-child(2) {
                  display: none;
                }
              }
              ul {
                padding-left: 0;
                li {
                  a {
                    display: inline-block;
                  }
                }
              }
            }
          }
          .menu-label:not(:last-child) {
            margin-bottom: 0;
          }
        }
      }
    }
  }
}
@media screen and (min-width: 1024px) {
  .b-sidebar {
    .sidebar-content {
      &.is-mini {
        &:not(.is-mini-expand),
        &.is-mini-expand:not(:hover):not(.is-mini-delayed) {
          .menu-list {
            li {
              a {
                span:nth-child(2) {
                  display: none;
                }
              }
              ul {
                padding-left: 0;
                li {
                  a {
                    display: inline-block;
                  }
                }
              }
            }
          }
          .menu-label:not(:last-child) {
            margin-bottom: 0;
          }
        }
      }
    }
  }
}
.is-mini-expand {
  .menu-list a {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}
</style>
