<template>
  <div>
    <section class="hero">
      <div class="hero-body"></div>
    </section>
    <div class="tile is-ancestor mx-3">
      <div class="tile is-3">
        <div class="box has-background-dark">
          <div class="card-header">
            <p class="card-header-title has-text-white">Prefix</p>
          </div>
          <p class="card-header-title has-text-white">
            <span class="tag is-black is-medium">{{ this.guildPrefix }}</span>
          </p>
          <b-field class="mx-4 mb-3 has-text-white">
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
      <div class="tile is-parent">
        <div class="tile is-child box has-background-dark mx-3">
          <div class="card-header">
            <p class="card-header-title has-text-white">Welcome Message</p>
          </div>
          <div class="box has-background-black">
            <div class="content is-black my-2">
              {{ this.guildWelcomeMessage }}
            </div>
          </div>
          <b-field class="mx-3 mb-3 has-text-white">
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
    </div>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'
import AssignableRoles from '~/components/wiki/AssignableRoles.vue'
import dashboard from '~/layouts/dashboard.vue'

export default Vue.extend({
  components: { dashboard, AssignableRoles },
  layout: 'dashboard',
  data() {
    let guildId: string = ''
    let guildPrefix: string = ''
    let inputPrefix: string = ''
    let guildWelcomeMessage: string = ''
    let inputWelcomeMessage: string = ''

    return {
      inputPrefix,
      guildId,
      guildPrefix,
      guildWelcomeMessage,
      inputWelcomeMessage,
    }
  },

  mounted() {
    this.guildId = this.$route.params.id
  },

  async fetch() {
    let guildId = this.$route.params.id
    this.guildPrefix =
      (await this.$api.customPrefix.getCustomPrefix(guildId)) ??
      this.$config.defaultPrefix

    this.guildWelcomeMessage =
      (await this.$api.welcomeMessage.getWelcomeMessage(guildId)) ??
      'No Welcome Message set'
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
  },
})
</script>

<style lang="scss">
#white-text {
  color: white;
}
</style>
