<template>
  <div>
    <h1 class="title is-3">Tags</h1>
    <div class="content">
      <h3 class="title is-light">Overview</h3>
      <p>
        Tags are custom commands that allow for users to create custom responses
        to a given tag name. Simply add a tag and then invoke it with either
        command notation or inline notation and ClemBot will respond with that
        tags content in a given channel.
      </p>
      <p>
        ClemBots Tags support the idea of ownership, if a user creates a tag,
        that tag is owned by them until they either leave the server or transfer
        the tag to someone else. By owning the tag they are allowed to either
        edit or delete the tag. When a user leaves a server all their owned tags
        become unclaimed and are free to be claimed by anyone else in the
        server.
      </p>
      <p>
        ClemBot also tracks what tags are popular and allows for you to access
        that information, you can view the total number of uses of a tag as well
        as its owner and creation date with the info command!
      </p>
      <h2 class="title is-light">Use a tag</h2>
      <h4 class="title is-light">Command Notation</h4>
      <blockquote class="has-background-grey-darker">
        !tag &lt;TagName&gt;
      </blockquote>
      <h4 class="title is-light">Inline Notation</h4>
      <p>
        Inline notation is handled by prefixing a word with '$' in a given
        message. If ClemBot finds a matching tag it will respond with that tags
        content.
      </p>
      <blockquote class="has-background-grey-darker">
        Hello there Discord, I am invoking $MyTag isnt that cool!
      </blockquote>
      <h2 class="title is-light">Commands</h2>
      <h4 class="title is-light">View all tags in the server</h4>
      <blockquote class="has-background-grey-darker">!tags</blockquote>
      <h4 class="title is-light">Create a tag</h4>
      <p>Format</p>
      <blockquote class="has-background-grey-darker">
        !tag add &lt;TagName&gt; &lt;TagContent&gt;
      </blockquote>
      <p>Example</p>
      <blockquote class="has-background-grey-darker">
        !tag add MyTag ClemBot is an awesome bot!
      </blockquote>
      <h4 class="title is-light">Edit a tag</h4>
      <p>Format</p>
      <blockquote class="has-background-grey-darker">
        !tag edit &lt;TagName&gt; &lt;NewTagContent&gt;
      </blockquote>
      <p>Example</p>
      <blockquote class="has-background-grey-darker">
        !tag add MyTag ClemBot is the best bot ever!!!
      </blockquote>
      <h4 class="title is-light">Delete a tag</h4>
      <p>Format</p>
      <blockquote class="has-background-grey-darker">
        !tag delete &lt;TagName&gt;
      </blockquote>
      <p>Example</p>
      <blockquote class="has-background-grey-darker">
        !tag delete MyTag
      </blockquote>
      <h4 class="title is-light">Get a tags info</h4>
      <p>Format</p>
      <blockquote class="has-background-grey-darker">
        !tag info &lt;TagName&gt;
      </blockquote>
      <p>Example</p>
      <blockquote class="has-background-grey-darker">
        !tag info MyTag
      </blockquote>
      <h4 class="title is-light">Claim a tag</h4>
      <p>Format</p>
      <blockquote class="has-background-grey-darker">
        !tag claim &lt;TagName&gt;
      </blockquote>
      <p>Example</p>
      <blockquote class="has-background-grey-darker">
        !tag claim MyTag
      </blockquote>
      <h4 class="title is-light">Transfer ownership of a tag</h4>
      <p>Format</p>
      <blockquote class="has-background-grey-darker">
        !tag transfer &lt;TagName&gt; &lt;NewOwner&gt;
      </blockquote>
      <p>Example</p>
      <blockquote class="has-background-grey-darker">
        !tag transfer MyTag @SomeOtherUser
      </blockquote>
      <h4 class="title is-light">View all unclaimed tags</h4>
      <p>Example</p>
      <blockquote class="has-background-grey-darker">!tag unclaimed</blockquote>
    </div>
  </div>
</template>
