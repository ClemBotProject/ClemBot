<template>
  <div>
    <h1 class="title is-3">Designated Channels</h1>
    <div class="content">
      <h3 class="title is-light">Overview</h3>
      <p>
        ClemBot provides multiple different logging solutions for all aspects of
        your server, the way that ClemBot allows you to configure this is
        through a concept called Designated Channels. There are multiple
        possible designations for different events that ClemBot processes. You
        may add these designations to as many channels within your server as you
        would like. A channel can also have multiple designations at once.
      </p>
      <h4 class="title is-light">Available Designations</h4>
      <b-table :data="channels" :columns="columns"></b-table>
      <h2 class="title is-light">Commands</h2>
      <h3 class="title is-light">
        View all channel designations in the server
      </h3>
      <blockquote class="has-background-grey-darker">!channels</blockquote>
      <h3 class="title is-light">Add a designation to a channel</h3>
      <p><b>Format</b></p>
      <blockquote class="has-background-grey-darker">
        !channel add &lt;DesignationName&gt; #ChannelName
      </blockquote>
      <p><b>Example</b></p>
      <blockquote class="has-background-grey-darker">
        !channel add message_log #General
      </blockquote>
      <h3 class="title is-light">Remove a designation from a channel</h3>
      <p><b>Format</b></p>
      <blockquote class="has-background-grey-darker">
        !channel delete &lt;DesignationName&gt; #ChannelName
      </blockquote>
      <p><b>Example</b></p>
      <blockquote class="has-background-grey-darker">
        !channel delete message_log #General
      </blockquote>
    </div>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'

interface Channel {
  name: string
  description: string
}

export default Vue.extend({
  data() {
    const channels: Array<Channel> = [
      {
        name: 'message_log',
        description:
          'Channel for Clembot to log all message edits and deletions',
      },
      {
        name: 'moderation_log',
        description:
          'Channel for Clembot to send a log of all moderation actions that happen in the server',
      },
      {
        name: 'user_join_log',
        description:
          'Channel for Clembot to log all users that join the server',
      },
      {
        name: 'user_leave_log',
        description:
          'Channel for Clembot to log all users that leave the server',
      },
      {
        name: 'starboard',
        description:
          'Channel to allow for starred messages to be immortalized for eternity',
      },
    ]
    return {
      channels: channels.sort((a, b) =>
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
