<template>
  <div>
    <h1 class="title is-3">Assignable Roles</h1>
    <div class="content">
      <h3 class="title is-light">Overview</h3>
      <p>
        Servers often have many roles that regular users can have, but might not
        want to give all users access to all roles, but it can be annoying to
        manually give people the roles they want. ClemBot provides a way to mark
        roles as assignable so that normal users can add and remove that as they
        please with a simpe command.
      </p>
      <h2 class="title is-light">Commands</h2>
      <h4 class="title is-light">View all assignable roles</h4>
      <p>Example</p>
      <blockquote class="has-background-grey-darker">!roles</blockquote>
      <h4 class="title is-light">
        Add an assignable role to yourself, or remove an assignable role from
        yourself
      </h4>
      <p>Format</p>
      <blockquote class="has-background-grey-darker">
        !role &lt;RoleName&gt;
      </blockquote>
      <p>Example</p>
      <blockquote class="has-background-grey-darker">
        !role @MyAwesomeRole
      </blockquote>
      <h4 class="title is-light">Mark a role as assignable</h4>
      <p>
        <b>Note:</b> This is the admin command to <b>MARK</b> a role as
        assignable. If you would like to give yourself a role please see the
        above section on adding an assignable role to yourself
      </p>
      <p>Format</p>
      <blockquote class="has-background-grey-darker">
        !role add &lt;RoleName&gt;
      </blockquote>
      <p>Example</p>
      <blockquote class="has-background-grey-darker">
        !role add @MyAwesomeRole
      </blockquote>
      <h4 class="title is-light">Remove a role as assignable</h4>
      <p>
        <b>Note:</b> This is the admin command to <b>REMOVE</b> a role as
        assignable. If you would like to remove a role from yourself please see
        the above section on removing an assignable role from yourself
      </p>
      <p>Format</p>
      <blockquote class="has-background-grey-darker">
        !role delete &lt;RoleName&gt;
      </blockquote>
      <p>Example</p>
      <blockquote class="has-background-grey-darker">
        !role delete @MyAwesomeRole
      </blockquote>
    </div>
  </div>
</template>
