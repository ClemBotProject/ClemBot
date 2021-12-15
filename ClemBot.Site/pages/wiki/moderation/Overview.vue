<template>
  <div>
    <h1 class="title is-3">Moderation Overview</h1>
    <div class="content">
      <p></p>
      <h1 class="title is-light">Overview</h1>
      <p>
        ClemBot provides powerful moderation tools to help you run your server.
        Every moderation action is logged and categorized and can be searched
        through at any time. With support for all the standard commands and more
        coming soon!!
      </p>
      <p>
        You have a complete history of every Infraction every committed in your
        server, to view them run these comands.
      </p>
      <h2 class="title is-light">Commands</h2>
      <h4 class="title is-light">View Infractions</h4>
      <blockquote class="has-background-grey-darker">
        !infractions @User
      </blockquote>
      <h4 class="title is-light">Delete Infraction</h4>
      <blockquote class="has-background-grey-darker">
        !infractions remove &lt;InfractionId&gt;
      </blockquote>
      <p>
        To find the infraction id run the infractions command on a given user.
      </p>
    </div>
  </div>
</template>
