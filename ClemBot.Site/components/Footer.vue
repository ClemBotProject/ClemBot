<template>
  <footer class="footer has-background-dark has-text-centered">
    <a
      href="https://github.com/ClemBotProject/ClemBot"
      rel="noopener noreferrer"
      target="_blank"
    >
      <div class="tile mt-6 is-parent column">
        <article
          id="repo-footer"
          class="tile is-child notification has-background-black"
        >
          <p class="title">Open Source</p>
          <p class="subtitle">
            MIT licensed with an active and helpful community
          </p>
        </article>
      </div>
    </a>
    <div>
      <a
        href="https://discord.gg/mhrVuyh"
        rel="noopener noreferrer"
        target="_blank"
        >Support Server</a
      >
    </div>
    <div>
      <nuxt-link :to="{ path: '/privacy' }">Privacy Policy</nuxt-link>
    </div>
    <div>
      <a
        href="https://github.com/ClemBotProject/ClemBot/blob/master/LICENSE"
        rel="noopener noreferrer"
        target="_blank"
        >License</a
      >
    </div>
    <a href="https://vuejs.org/">
      <img
        src="https://raw.githubusercontent.com/vuejs/art/master/white-on-dark-logo.png"
        alt="Made with Bulma"
        class="mb-1"
        width="20"
        height="20"
      />
    </a>
    <a href="https://bulma.io">
      <img
        src="https://bulma.io/images/made-with-bulma--white.png"
        alt="Made with Bulma"
        width="128"
        height="24"
      />
    </a>
  </footer>
</template>
