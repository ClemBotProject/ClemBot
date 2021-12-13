<template>
  <div>
    <section class="section is-small"></section>
    <section class="section is-small">
      <sponsor-button />
    </section>
    <section class="section is-small box has-shadow">
      <contributors />
    </section>
    <section class="section is-small box has-shadow">
      <stargazers />
    </section>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'
import SponsorButton from '~/components/support/SponsorButton.vue'
import Stargazers from '~/components/support/Stargazers.vue'
import Contributors from '~/components/support/Contributors.vue'

export default Vue.extend({
 
})
</script>
