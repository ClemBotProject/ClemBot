<template>
  <div>
    <h1 class="title is-3">Bans</h1>
    <div class="content">
      <p>
        Bans remove an individual from a server permanently and block their IP
        from rejoining. Allows for optionally specifying the number of days of messages from which to purge a users messages.
		(Defaults to 0 with a maximum of 7)
      </p>
      <h4 class="title is-light">Format</h4>
      <blockquote class="has-background-grey-darker">
        !ban @User &lt;DaysToPurge&gt; &lt;Reason&gt;
      </blockquote>
      <p><b>Example</b></p>
      <blockquote class="has-background-grey-darker">
        !ban @User Spamming and trolling
      </blockquote>
      <blockquote class="has-background-grey-darker">
        !ban @User 3 Spamming and trolling
      </blockquote>
    </div>
  </div>
</template>
