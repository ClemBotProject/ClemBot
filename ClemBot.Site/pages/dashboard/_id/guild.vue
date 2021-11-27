<template>
  <section class="hero">
    <div class="hero-body"></div>
    <div class="card has-background-dark mx-6">
      <div class="card-header">
        <p class="card-header-title has-text-white">Current Prefix </p>
      </div>
        <p class="card-header-title has-text-white">{{ this.guildPrefix }} </p>
      <b-field class="mx-4 mb-3 has-text-white">
        <template #label>
          <span class="has-text-white">Set</span>
        </template>
        <b-input id="form" class="has-text-white" v-model="name"></b-input>
      </b-field>
    </div>
  </section>
</template>

<script lang="ts">
import Vue from 'vue'
export default Vue.extend({
  data() {
    let guildPrefix: string = ''
    let guildId: string = ''
    return {
        guildId,
        guildPrefix
    }
  },
  layout: 'dashboard',

  mounted() {
      this.guildId = this.$route.params.id
  },

  async fetch() {
      let guildId = this.$route.params.id
      this.guildPrefix = await this.$api.customPrefix.getCustomPrefix(guildId)
  }

})
</script>

<style lang="scss">
#form{
    color:white;
}
</style>
