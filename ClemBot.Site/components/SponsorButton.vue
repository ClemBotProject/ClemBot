<template>
  <div class="columns">
    <div
      id="sponsor-section"
      class="column is-half is-offset-one-quarter has-text-centered"
    >
      <h1 class="is-size-2">Sponsor Us On GitHub!!</h1>
      <div class="box">
        <b-button
          id="sponsor-button"
          type="is-primary"
          expanded
          icon-left="github-circle"
          tag="a"
          href="https://github.com/sponsors/ClemBotProject"
          target="_blank"
        >
          <b-icon icon="heart-outline" />
        </b-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
#sponsor-section {
  box-shadow: rgba(240, 46, 170, 0.4) 5px 5px, rgba(240, 46, 170, 0.3) 10px 10px,
    rgba(240, 46, 170, 0.2) 15px 15px, rgba(240, 46, 170, 0.1) 20px 20px,
    rgba(240, 46, 170, 0.05) 25px 25px;
  outline: white;
}
#sponsor-button {
  background-color: #db61a2;
}
</style>
