<template>
  <div>
    <h1 class="title is-3">Custom Prefix</h1>
    <div class="content">
      <h3 class="title is-light">Overview</h3>
      <p>
        A command prefix is the character or phrase that notifies ClemBot that
        you wish to invoke a command.
      </p>
      <h4 class="title is-light">Command Example</h4>
      <blockquote class="has-background-grey-darker">!about</blockquote>
      <p>
        "!" is the command prefix and <b>about</b> is the name of the command
        that you wish to invoke. <br /><br />
        To change the prefix that the bot responds to the <b>prefix</b> command
        should be invoked
      </p>
      <h4 class="title is-light">Command Format</h4>
      <blockquote class="has-background-grey-darker">
        &lt;CurrentPrefix&gt;prefix &lt;NewPrefix&gt;
      </blockquote>
      <h4 class="title is-light">Example</h4>
      <blockquote class="has-background-grey-darker">!prefix ?</blockquote>
      <p>or</p>
      <blockquote class="has-background-grey-darker">
        @ClemBot prefix ?
      </blockquote>
    </div>
  </div>
</template>
