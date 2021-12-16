<template>
  <div>
    <h1 class="title is-3">Mutes</h1>
    <div class="content">
      <p>
        Mutes silence an individual and prevent them from sending messages or
        joining voice channels for a given amount of time.
      </p>
      <h4 class="title is-light">Setup</h4>
      <p>
        Mutes require a one time inital setup for ClemBot to create the mute
        role and add it to all the channels. This might take a while depending
        on how many channels your server has. To avoid a heavy startup load the
        bot will prompt you to initialize the role when you run the mute command
        for the first time. After the initial setup is complete it will then
        apply the mute as normal.
      </p>
      <h4 class="title is-light">Format</h4>
      <blockquote class="has-background-grey-darker">
        !mute @User &lt;Duration&gt; &lt;Reason&gt;
      </blockquote>
      <p><b>Example</b></p>
      <blockquote class="has-background-grey-darker">
        !mute @User 1d1h Spamming and trolling
      </blockquote>
      <h4 class="title is-light">Duration String</h4>
      <p>
        ClemBot supports time strings to specify how long a mute should last.
        For example, to mute someone for 12 hours you would use the string
        <code>12h</code>. To mute someone for twelve days and thirty minutes you
        would use the string <code>12d30m</code>. And so on in any combination
        you would like.
      </p>
    </div>
  </div>
</template>
