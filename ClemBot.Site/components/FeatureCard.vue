<template>
  <div class="tile is-parent mx-3 mb-6 has-text-centered">
    <article id="feature-shadow" class="tile is-child notification">
      <p class="title">{{ title }}</p>
      <div class="divider">About</div>
      <div class="block">
        <p class="subtitle">
          {{ description }}
        </p>
      </div>

      <div class="has-shadow">
        <b-image id="help-image" :src="image" />
      </div>
    </article>
  </div>
</template>

<script lang="ts">
export default {
  props: {
    title: {
      type: String,
      required: true,
    },
    description: {
      type: String,
      required: true,
    },
    image: {
      type: String,
      required: true,
    },
  },
}
</script>

<style scoped>
#feature-shadow {
  box-shadow: rgba(0, 0, 0, 0.4) 0px 6px 7px,
    rgba(0, 0, 0, 0.3) 0px 7px 13px -3px, rgba(0, 0, 0, 0.2) 0px -3px 0px inset;

  background-color: #36393f;
}

.divider {
  color: #ffffff;
}
</style>
