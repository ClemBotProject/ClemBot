<template>
  <div class="card">
    <div class="columns is-centered is-vcentered">
      <div class="title is-5 has-text-light m-4">Github Stargazers</div>
      <iframe
        src="https://ghbtns.com/github-btn.html?user=ClemBotProject&repo=ClemBot&type=star&count=true&size=large"
        frameborder="0"
        scrolling="0"
        width="170"
        height="30"
        title="GitHub"
      ></iframe>
    </div>
    <div
      class="columns is-mobile is-gapless card-content is-multiline is-centered"
    >
      <div
        v-for="gazer in starGazers"
        :key="gazer"
        class="column is-1-tablet is-1-desktop is-2-mobile is-child"
      >
        <a :href="gazer.html_url">
          <b-image
            id="contributor-tile"
            class="m-2"
            tag="a"
            rounded="true"
            :src="gazer.avatar_url"
          ></b-image>
        </a>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'

interface StarGazer {
  id: number
  // eslint-disable-next-line camelcase
  avatar_url: string
  // eslint-disable-next-line camelcase
  html_url: string
}

export default Vue.extend({
  data() {
    const starGazers: Array<StarGazer> = []

    return { starGazers }
  },

  async fetch() {
    this.starGazers = await this.$api.$axios.$get<Array<StarGazer>>(
      'https://api.github.com/repos/ClemBotProject/ClemBot/stargazers?per_page=100'
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
