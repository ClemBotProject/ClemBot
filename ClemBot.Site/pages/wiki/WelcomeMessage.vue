<template>
  <div>
    <h1 class="title is-3">Welcome Messages</h1>
    <div class="content">
      <h3 class="title is-light">Overview</h3>
      <p>
        Welcome messages are a way to define a message that ClemBot will dm to
        all members that join your server. You can use this to notify users of
        any rules or setup they may need to know, or just say hello!
      </p>
      <h2 class="title is-light">Commands</h2>
      <h3 class="title is-light">View the current Welcome Message</h3>
      <blockquote class="has-background-grey-darker">!welcome</blockquote>
      <h4 class="title is-light">Set a welcome message</h4>
      <p>Format</p>
      <blockquote class="has-background-grey-darker">
        !welcome set &lt;Message&gt;
      </blockquote>
      <p>Example</p>
      <blockquote class="has-background-grey-darker">
        !welcome set Hello there, welcome to my server!
      </blockquote>
      <h3 class="title is-light">Remove the current welcome message</h3>
      <blockquote class="has-background-grey-darker">
        !welcome delete
      </blockquote>
    </div>
  </div>
</template>
