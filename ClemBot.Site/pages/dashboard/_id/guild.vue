<template>
  <section class="hero">
    <div class="hero-body"></div>
    <div class="tile is-ancestor is-vertical mx-6">
      <div class="tile is-ancestor">
        <div class="card has-background-dark">
          <div class="card-header">
            <p class="card-header-title has-text-white">Current Prefix</p>
          </div>
          <p class="card-header-title has-text-white">{{ this.guildPrefix }}</p>
          <b-field class="mx-4 mb-3 has-text-white">
            <template #label>
              <span class="has-text-white">Set</span>
            </template>
            <b-input
              id="form"
              class="has-text-white"
              autocomplete="off"
              v-model="name"
            ></b-input>
          </b-field>
          <div
            v-if="name != ''"
            @click="customPrefixSaveClick"
            class="card-content columns is-vcentered"
          >
            <div class="column">
              <b-button class="has-text-white">Save</b-button>
            </div>
          </div>
        </div>
        <div class="card has-background-dark mx-3">
          <div class="card-header">
            <p class="card-header-title has-text-white">Current Welcome Message</p>
          </div>
          <p class="card-header-title has-text-white">{{ this.guildPrefix }}</p>
          <b-field class="mx-4 mb-3 has-text-white">
            <template #label>
              <span class="has-text-white">Set</span>
            </template>
            <b-input
              id="form"
              class="has-text-white"
              autocomplete="off"
              v-model="name"
            ></b-input>
          </b-field>
          <div
            v-if="name != ''"
            @click="customPrefixSaveClick"
            class="card-content columns is-vcentered"
          >
            <div class="column">
              <b-button class="has-text-white">Save</b-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script lang="ts">
import Vue from 'vue'
import { chunkArray } from '~/services/Utilities'

export default Vue.extend({
  data() {
    let guildPrefix: string = ''
    let guildId: string = ''
    let name: string = ''
    return {
      name,
      guildId,
      guildPrefix,
    }
  },
  layout: 'dashboard',

  mounted() {
    this.guildId = this.$route.params.id
  },

  async fetch() {
    let guildId = this.$route.params.id
    this.guildPrefix =
      (await this.$api.customPrefix.getCustomPrefix(guildId)) ??
      this.$config.defaultPrefix
  },

  methods: {
    async customPrefixSaveClick() {
      await this.$api.customPrefix.setCustomPrefix(this.guildId, this.name)
      this.guildPrefix = await this.$api.customPrefix.getCustomPrefix(
        this.guildId
      )
      this.name = ''
    },
  },
})
</script>

<style lang="scss">
#form {
  color: white;
}
</style>
