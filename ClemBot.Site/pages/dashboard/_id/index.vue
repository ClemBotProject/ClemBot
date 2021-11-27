<template>
  <section class="hero">
    <div class="hero-body">{{ this.$route.params.id }}</div>
  </section>
</template>

<script lang="ts">
import Vue from 'vue'
export default Vue.extend({
  layout: 'dashboard',
})
</script>
