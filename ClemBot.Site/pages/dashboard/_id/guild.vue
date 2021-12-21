<template>
  <div>
    <b-message
      class="mb-3"
      size="is-primary"
      type="is-primary-light"
      :closable="false"
      title="Guild Options"
    />
    <div class="tile is-ancestor mx-3 my-2">
      <div class="tile is-3">
        <div class="box has-background-dark">
          <div class="card-header my-2">
            <p class="card-header-title has-text-white">Command Prefix</p>
          </div>
          <p class="card-header-title has-text-white">
            <span class="tag is-black is-medium">{{ this.guildPrefix }}</span>
          </p>
          <b-field v-if="canSetPrefix" class="mx-4 mb-3 has-text-white">
            <template #label>
              <span class="has-text-white">Set</span>
            </template>
            <b-input
              id="white-text"
              class="has-text-white"
              autocomplete="off"
              v-model="inputPrefix"
            ></b-input>
          </b-field>
          <div
            v-if="inputPrefix != ''"
            @click="customPrefixSaveClick"
            class="card-content columns is-vcentered"
          >
            <div class="column">
              <b-button class="has-text-white">Save</b-button>
            </div>
          </div>
        </div>
      </div>
      <div v-if="canSeeWelcomeMessage" class="tile is-parent">
        <div class="tile is-child box has-background-dark mx-3">
          <div class="card-header my-2">
            <p class="card-header-title has-text-white">Welcome Message</p>
          </div>
          <div class="box has-background-black">
            <div class="content is-black my-2">
              {{ this.guildWelcomeMessage }}
            </div>
          </div>
          <b-field v-if="canSetWelcomeMessage" class="mx-3 mb-3 has-text-white">
            <template #label>
              <span class="has-text-white">Set</span>
            </template>
            <b-input
              id="white-text"
              type="textarea"
              class="has-text-white"
              maxlength="2000"
              autocomplete="off"
              v-model="inputWelcomeMessage"
            ></b-input>
          </b-field>
          <div
            v-if="inputWelcomeMessage != ''"
            @click="customWelcomeMessageSaveClick"
            class="card-content columns is-vcentered"
          >
            <div class="column">
              <b-button class="has-text-white">Save</b-button>
            </div>
          </div>
        </div>
      </div>
      <div v-if="canSeeGuildConfig" class="tile is-parent">
        <div class="tile is-child box has-background-dark mx-3">
          <div class="card-header my-2">
            <p class="card-header-title has-text-white">Guild Config</p>
          </div>
          <div class="box has-background-black">
            <div class="content is-black my-2">
              <b-field>
                <b-switch
                  :disabled="!canSeeGuildConfig"
                  v-model="canEmbedLinks"
                  @input="embedMessageSwitch"
                  type="is-success"
                >
                  Allow message link embeds</b-switch
                >
              </b-field>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'
import dashboard from '~/layouts/dashboard.vue'
import { BotAuthClaims } from '~/services/Claims'

export default Vue.extend({
  components: { dashboard },
  layout: 'dashboard',
  data() {
    let guildId: string = ''
    let guildPrefix: string = ''
    let inputPrefix: string = ''
    let guildWelcomeMessage: string = ''
    let inputWelcomeMessage: string = ''
    let canEmbedLinks: boolean = false

    return {
      inputPrefix,
      guildId,
      guildPrefix,
      guildWelcomeMessage,
      inputWelcomeMessage,
      canEmbedLinks,
    }
  },

  computed: {
    canSeeWelcomeMessage: function (): boolean {
      return this.hasClaim(BotAuthClaims.welcomeMessageView)
    },

    canSetWelcomeMessage: function (): boolean {
      return this.hasClaim(BotAuthClaims.welcomeMessageModify)
    },

    canSetPrefix: function (): boolean {
      return this.hasClaim(BotAuthClaims.customPrefixSet)
    },

    canSeeGuildConfig: function (): boolean {
      return this.hasClaim(BotAuthClaims.guildSettingsView)
    },

    canEditGuildConfig: function (): boolean {
      return this.hasClaim(BotAuthClaims.guildSettingsEdit)
    },
  },

  mounted() {
    this.guildId = this.$route.params.id
  },

  async fetch() {
    let guildId = this.$route.params.id
    try {
      this.guildPrefix =
        (await this.$api.customPrefix.getCustomPrefix(guildId)) ??
        this.$config.defaultPrefix
    } catch (e) {
      console.log(e)
      this.guildPrefix = 'Retrieving Guild Prefix failed'
    }

    try {
      if (this.canSeeWelcomeMessage){
        this.guildWelcomeMessage =
          (await this.$api.welcomeMessage.getWelcomeMessage(guildId)) ??
          'No Welcome Message set'
      }
    } catch (e) {
      console.log(e)
      this.guildWelcomeMessage = 'Retrieving Guild Welcome message failed'
    }

    try {
      if (this.canSeeGuildConfig){
        this.canEmbedLinks =
          (await this.$api.guildSettings.getCanEmbedLink(guildId)) ?? false
      }
    } catch (e) {
      console.log(e)
    }
  },

  methods: {
    async customPrefixSaveClick() {
      await this.$api.customPrefix.setCustomPrefix(
        this.guildId,
        this.inputPrefix
      )
      this.guildPrefix = await this.$api.customPrefix.getCustomPrefix(
        this.guildId
      )
      this.inputPrefix = ''
    },

    async customWelcomeMessageSaveClick() {
      await this.$api.welcomeMessage.setWelcomeMessage(
        this.guildId,
        this.inputWelcomeMessage
      )
      this.guildWelcomeMessage =
        await this.$api.welcomeMessage.getWelcomeMessage(this.guildId)
      this.inputWelcomeMessage = ''
    },

    async embedMessageSwitch() {
      await this.$api.guildSettings.setCanEmbedLink(this.guildId, this.canEmbedLinks)
      this.canEmbedLinks = await this.$api.guildSettings.getCanEmbedLink(this.guildId)
    },

    hasClaim(claim: BotAuthClaims): boolean {
      // @ts-ignore
      let guildId: string = this.$route.params.id
      // @ts-ignore
      let activeGuild = this.$auth.user?.guilds.filter(
        (x: { id: string }) => x.id == guildId
      )[0]
      return activeGuild.claims.find((x: string) => x === claim)
    },
  },
})
</script>

<style lang="scss">
#white-text {
  color: white;
}
</style>
