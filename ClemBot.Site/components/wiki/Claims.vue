<template>
  <div>
    <h1 class="title is-3">Authorization Claims</h1>
    <div class="content">
      <h3 class="title is-light">Overview</h3>
      <p>
        By default ClemBot allows for anyone with the Admin permission in
        Discord full access to ClemBots functionality. But if you want to grant
        people without Admin permissions access to individual parts of the bot
        (a team of moderators for example) you can do that through "Claims".
        <br />
        <br />
        Claims are ClemBots way of providing servers incredibly granular and
        precise control over <b>WHO</b> has access to different parts of
        ClemBot. Claims are added to roles within your server. Anyone who has a
        role that has associated claims is granted access to the functionality
        of the bot that the claim correlates too. A role can have multiple
        claims on it and a claim can be on multiple roles, how you set up your
        server is up too you!
      </p>
      <h4 class="title is-light">Available Claims</h4>
      <b-table :data="availableClaims" :columns="columns"></b-table>
      <h2 class="title is-light">Commands</h2>
      <h3 class="title is-light">Add a claim to a role</h3>
      <p><b>Format</b></p>
      <blockquote class="has-background-grey-darker">
        !claims add &lt;ClaimName&gt; @Role
      </blockquote>
      <p><b>Example</b></p>
      <blockquote class="has-background-grey-darker">
        !claims add tag_add @MyCoolRole
      </blockquote>
      <h3 class="title is-light">Remove a claim from a role</h3>
      <p><b>Format</b></p>
      <blockquote class="has-background-grey-darker">
        !claims remove &lt;ClaimName&gt; @Role
      </blockquote>
      <p><b>Example</b></p>
      <blockquote class="has-background-grey-darker">
        !claims remove tag_add @MyCoolRole
      </blockquote>
      <h3 class="title is-light">View Claims on a role or user</h3>
      <p><b>Format</b></p>
      <blockquote class="has-background-grey-darker">!claims @Role</blockquote>
      <p>or</p>
      <blockquote class="has-background-grey-darker">!claims @User</blockquote>
      <p><b>Example</b></p>
      <blockquote class="has-background-grey-darker">
        !claims @Jayy <br />
        !claims @MyCoolRole
      </blockquote>
    </div>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'

interface Claim {
  name: string
  description: string
}

export default Vue.extend({
  data() {
    const claims: Array<Claim> = [
      {
        name: 'custom_prefix_set',
        description:
          'Allows for the prefix the Clembot responds to in a server to be set',
      },
      {
        name: 'claims_view',
        description: 'Allows for viewing of claims that a user or role has',
      },
      {
        name: 'claims_modify',
        description: 'Allows for modifying the assigned claims of a role',
      },
      {
        name: 'designated_channel_view',
        description:
          'Allows for viewing of available and assigned designated channels in a server',
      },
      {
        name: 'designated_channel_modify',
        description:
          'Allows for adding and removing designations from channels in a server',
      },
      {
        name: 'tag_add',
        description: 'Allows for adding a tag in a server',
      },
      {
        name: 'tag_delete',
        description: 'Allows for deleting other peoples tags in a server',
      },
      {
        name: 'assignable_roles_add',
        description: 'Allows for marking a role as assignable',
      },
      {
        name: 'assignable_roles_delete',
        description: 'Allows for removing a role as assignable',
      },
      {
        name: 'delete_message',
        description:
          'Allows for deletion of any message that Clembot reacts with a trashcan too',
      },
      {
        name: 'moderation_warn',
        description: 'Allows for usage of the warn command',
      },
      {
        name: 'moderation_mute',
        description: 'Allows for usage of the mute command',
      },
      {
        name: 'moderation_ban',
        description: 'Allows for usage of the ban command',
      },
      {
        name: 'moderation_infraction_view',
        description:
          'Allows for usage of the infractions command to list a given users warnings',
      },
    ]

    return {
      availableClaims: claims.sort((a, b) =>
        a.name > b.name ? 1 : b.name > a.name ? -1 : 0
      ),
      columns: [
        {
          field: 'name',
          label: 'Name',
        },
        {
          field: 'description',
          label: 'Description',
        },
      ],
    }
  },
})
</script>
