<template>
  <div>
    <b-image
      class="is-32x32"
      rounded
      :src="url"
    />
  </div>
</template>

<script lang="ts">
import Vue from 'vue'

export default Vue.extend({
  data() {
    let url = ''
    return { url }
  },
  mounted() {
    try {
      // @ts-ignore
      this.url = `https://cdn.discordapp.com/avatars/${this.$auth.user.user.user.id}/${this.$auth.user.user.user.avatar}.png?size=128`
    }
    catch {
      this.url = 'https://cdn.discordapp.com/embed/avatars/0.png'
    }
  }
})
</script>