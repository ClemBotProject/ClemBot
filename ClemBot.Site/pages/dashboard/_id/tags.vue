<template>
  <section class="hero">
    <b-table
      :data="this.tags"
      :columns="[
        {
          field: 'name',
          label: 'First Name',
        },
        {
          field: 'content',
          label: 'Last Name',
        },
      ]"
    ></b-table>
  </section>
</template>

<script lang="ts">
import Vue from 'vue'
import { Tag } from '~/services/api/routes/Tags'

export default Vue.extend({
  layout: 'dashboard',
  data() {
    let tags: Array<Tag> = []

    return {
      tags,
    }
  },

  async fetch() {
    let guildId = this.$route.params.id
    this.tags = (await this.$api.tags.getGuildTags(guildId)) ?? []
  },
})
</script>
