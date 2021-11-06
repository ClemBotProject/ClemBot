<template>
  <div class="card">
    <div class="title is-5 has-text-light m-4">Code Contributors</div>
    <div
      class="columns is-mobile is-gapless card-content is-multiline is-centered"
    >
      <div
        v-for="contributor in contributors"
        :key="contributor"
        class="column is-1-tablet is-1-desktop is-2-mobile is-child"
      >
        <a :href="contributor.html_url">
          <b-image
            id="contributor-tile"
            class="m-2"
            tag="a"
            rounded="true"
            :src="contributor.avatar_url"
          ></b-image>
        </a>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'

interface Contributor {
  id: number
  // eslint-disable-next-line camelcase
  avatar_url: string
  // eslint-disable-next-line camelcase
  html_url: string
}

export default Vue.extend({
  data() {
    const contributors: Array<Contributor> = []

    return { contributors }
  },

  async fetch() {
    this.contributors = await this.$api.$axios.$get<Array<Contributor>>(
      'https://api.github.com/repos/ClemBotProject/ClemBot/contributors'
    )
  },
})
</script>

<style scoped>
#contributor-tile {
  -webkit-transition: all 0.1s ease-in-out;
  -moz-transition: all 0.1s ease-in-out;
  -ms-transition: all 0.1s ease-in-out;
  -o-transition: all 0.1s ease-in-out;
  transition: all 0.1s ease-in-out;
}

#contributor-tile :hover {
  -webkit-transition: all 0.1s ease-in-out;
  -moz-transition: all 0.1s ease-in-out;
  -o-transition: all 0.1s ease-in-out;
  transition: all 0.1s ease-in-out;
  -ms-transform: scale(1.08, 1.08);
  /* IE 9 */
  -webkit-transform: scale(1.08, 1.08);
  /* Safari */
  transform: scale(1.08, 1.08);
}
</style>
